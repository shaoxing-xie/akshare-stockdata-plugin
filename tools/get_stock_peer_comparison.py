from collections.abc import Generator
from typing import Any
import pandas as pd

import akshare as ak
from provider.akshare_stockdata import safe_ak_call, build_error_payload
from provider.akshare_registry import get_interface_config, normalize_symbol_with_market_prefix, normalize_symbol_with_uppercase_prefix
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .common_utils import (
    process_dataframe_output, 
    process_other_output, 
    handle_empty_result, 
    validate_required_params, 
    handle_akshare_error, 
    validate_stock_symbol,
    validate_period,
    validate_date_range,
    validate_adjust,
    process_symbol_format
)


class GetStockPeerComparisonTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetStockPeerComparisonTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            symbol = tool_parameters.get("symbol", "")
            
            logging.info(f"Interface: {interface}, Symbol: {symbol}")
            
            # 验证必需参数
            if not interface:
                yield self.create_text_message("请选择要调用的接口")
                yield self.create_json_message({"error": "interface required", "received_params": tool_parameters})
                return
                
            if not symbol:
                yield self.create_text_message("请提供股票代码")
                yield self.create_json_message({"error": "symbol required", "received_params": tool_parameters})
                return
            
            # 验证股票代码格式
            validation_result = None
            for result in validate_stock_symbol(symbol, self):
                if isinstance(result, bool):
                    validation_result = result
                else:
                    yield result
            if validation_result is False:
                return
                
        except Exception as e:
            logging.error(f"Error in _invoke start: {e}")
            yield self.create_text_message(f"参数处理错误: {e}")
            yield self.create_json_message({"error": f"parameter processing error: {e}"})
            return
        
        # 定义接口配置 - 从原工具迁移
        interface_configs = {
            "stock_zh_growth_comparison_em": {
                "fn": ak.stock_zh_growth_comparison_em,
                "requires_symbol": True,
                "supports_timeout": True,
                "description": "东方财富网-同行比较-成长性比较-指定股票"
            },
            "stock_zh_valuation_comparison_em": {
                "fn": ak.stock_zh_valuation_comparison_em,
                "requires_symbol": True,
                "supports_timeout": True,
                "description": "东方财富网-同行比较-估值比较-指定股票"
            },
            "stock_zh_dupont_comparison_em": {
                "fn": ak.stock_zh_dupont_comparison_em,
                "requires_symbol": True,
                "supports_timeout": True,
                "description": "东方财富网-同行比较-杜邦分析比较-指定股票"
            },
            "stock_zh_scale_comparison_em": {
                "fn": ak.stock_zh_scale_comparison_em,
                "requires_symbol": True,
                "supports_timeout": True,
                "description": "东方财富网-同行比较-公司规模-指定股票"
            },
        }
        
        # 获取接口配置
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"未知的接口: {interface}")
            yield self.create_json_message({"error": f"unknown interface: {interface}"})
            return
        
        try:
            # 网络参数 - 统一处理逻辑 - 从原工具迁移
            retries = int(tool_parameters.get("retries", 5))
            timeout_param = tool_parameters.get("timeout")  # 让子进程根据接口类型自动决定超时时间
            timeout = float(timeout_param) if timeout_param is not None else None
            logging.info(f"Network params - retries: {retries}, timeout: {timeout} (auto-determined by interface type)")
            
            # 构建调用参数 - 根据接口要求动态构建 - 从原工具迁移
            call_params = {}
            
            # 只有当接口需要symbol参数时才添加
            if config.get("requires_symbol", False):
                # 从akshare_registry获取接口配置，确定使用哪个预处理函数
                from provider.akshare_registry import REGISTRY, normalize_symbol
                registry_config = REGISTRY.get(interface, {})
                symbol_params = registry_config.get("params", {}).get("required", {}).get("symbol", {})
                preprocess_func = symbol_params.get("preprocess", "normalize_symbol")
                
                # 根据预处理函数选择相应的处理函数
                if preprocess_func == "normalize_symbol_with_uppercase_prefix":
                    processed_symbol = normalize_symbol_with_uppercase_prefix(symbol)
                elif preprocess_func == "normalize_symbol_with_market_prefix":
                    processed_symbol = normalize_symbol_with_market_prefix(symbol)
                else:  # 默认使用纯数字格式
                    processed_symbol = normalize_symbol(symbol)
                
                call_params["symbol"] = processed_symbol
            
            logging.info(f"Call params: {call_params}")
            logging.info(f"Function: {config['fn']}")
            
            # 调用AKShare接口 - timeout现在仅用于子进程超时控制 - 从原工具迁移
            try:
                result = safe_ak_call(
                    config["fn"],
                    retries=retries,
                    timeout=timeout,
                    **call_params
                )
            except Exception as e:
                # 检查是否是SSL连接错误 - 从原工具迁移
                error_msg = str(e)
                if any(keyword in error_msg for keyword in ["SSLError", "SSL", "HTTPSConnectionPool", "Max retries exceeded"]):
                    yield self.create_text_message(f"网络连接超时：\n\n{error_msg}\n\n这通常是由于以下原因：\n1. 数据量较大，需要较长时间获取\n2. 网络连接不稳定或SSL握手失败\n3. 数据源服务器响应较慢\n\n建议：\n1. 稍后重试（数据源可能暂时繁忙）\n2. 检查网络连接稳定性\n3. 尝试使用其他接口")
                    yield self.create_json_message({
                        "error": "ssl_timeout_error",
                        "message": "SSL连接超时，数据获取失败",
                        "details": error_msg,
                        "suggestion": "稍后重试或尝试其他接口"
                    })
                    return
                else:
                    # 使用统一的错误处理机制 - 从原工具迁移
                    yield from handle_akshare_error(e, self, f"股票代码: {symbol}, 接口: {interface}", str(timeout))
                    return
            
            # 处理结果 - 从原工具迁移
            if result is None:
                yield from handle_empty_result(self)
                return
            
            # 检查是否为空
            if hasattr(result, 'empty') and result.empty:
                yield from handle_empty_result(self)
                return
            
            # 输出处理 - 从原工具迁移
            if isinstance(result, pd.DataFrame):
                yield from process_dataframe_output(result, self)
            else:
                yield from process_other_output(result, self)
                
        except Exception as e:
            import logging
            logging.error(f"GetStockPeerComparisonTool error: {e}")
            text, payload = build_error_payload(e)
            yield self.create_text_message(text)
            yield self.create_json_message(payload)
            return

