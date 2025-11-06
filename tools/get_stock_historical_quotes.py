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


class GetStockHistoricalQuotesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetStockHistoricalQuotesTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            symbol = tool_parameters.get("symbol", "")
            period = tool_parameters.get("period", "")  # 周期（历史行情类）
            start_date = tool_parameters.get("start_date", "")
            end_date = tool_parameters.get("end_date", "")
            adjust = tool_parameters.get("adjust", "")
            
            logging.info(f"Interface: {interface}, Symbol: {symbol}, Period: {period}, Start: {start_date}, End: {end_date}, Adjust: {adjust}")
            
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
            "stock_zh_a_hist": {
                "fn": ak.stock_zh_a_hist,
                "requires_symbol": True,
                "requires_period": True,
                "period_type": "historical",  # 历史行情类
                "requires_date_range": True,
                "requires_adjust": True,
                "description": "东方财富网-沪深京A股-日频率数据-指定股票、周期、复权方式和指定日期区间"
            },
            "stock_zh_a_hist_tx": {
                "fn": ak.stock_zh_a_hist_tx,
                "requires_symbol": True,
                "requires_period": False,
                "requires_date_range": True,
                "requires_adjust": True,
                "supports_timeout": True,
                "description": "腾讯证券-沪深京A股-历史行情日频率数据-指定股票、复权方式和日期区间"
            },
            "stock_zh_kcb_daily": {
                "fn": ak.stock_zh_kcb_daily,
                "requires_symbol": True,
                "requires_period": False,
                "requires_date_range": False,
                "requires_adjust": True,
                "supports_timeout": False,
                "description": "新浪财经-科创板股票历史行情数据-指定股票、复权方式"
            },
        }
        
        # 获取接口配置
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"未知的接口: {interface}")
            yield self.create_json_message({"error": f"unknown interface: {interface}"})
            return
        
        # 根据接口配置验证必需参数
        if config.get("requires_period", False):
            period_type = config.get("period_type", "")
            if period_type == "historical":
                if not period:
                    yield self.create_text_message("请选择周期（历史行情类）")
                    yield self.create_json_message({"error": "period required for historical data interface", "received_params": tool_parameters})
                    return
            
        if config.get("requires_date_range", False):
            if not start_date:
                yield self.create_text_message("请提供开始日期")
                yield self.create_json_message({"error": "start_date required", "received_params": tool_parameters})
                return
            if not end_date:
                yield self.create_text_message("请提供结束日期")
                yield self.create_json_message({"error": "end_date required", "received_params": tool_parameters})
                return
        
        # 验证周期参数（如果需要）
        if config.get("requires_period", False):
            period_type = config.get("period_type", "")
            if period_type == "historical" and period:
                validation_result = None
                for result in validate_period(period, self, interface):
                    if isinstance(result, bool):
                        validation_result = result
                    else:
                        yield result
                if validation_result is False:
                    return
        
        # 验证日期范围（如果需要）
        if config.get("requires_date_range", False) and start_date and end_date:
            validation_result = None
            for result in validate_date_range(start_date, end_date, self):
                if isinstance(result, bool):
                    validation_result = result
                else:
                    yield result
            if validation_result is False:
                return
        
        # 验证调整参数（如果提供）
        if adjust:
            validation_result = None
            for result in validate_adjust(adjust, self):
                if isinstance(result, bool):
                    validation_result = result
                else:
                    yield result
            if validation_result is False:
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
            
            # 根据接口要求添加参数 - 从原工具迁移
            if config.get("requires_period", False):
                period_type = config.get("period_type", "")
                if period_type == "historical":
                    call_params["period"] = period
            
            if config.get("requires_date_range", False):
                call_params["start_date"] = start_date
                call_params["end_date"] = end_date
            
            if config.get("requires_adjust", False):
                if adjust == "none":
                    call_params["adjust"] = ""  # "none" 对应空字符串，表示不复权
                elif adjust:
                    call_params["adjust"] = adjust
            
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
                # 检查是否是SSL连接错误（历史数据接口也可能遇到） - 从原工具迁移
                error_msg = str(e)
                if any(keyword in error_msg for keyword in ["SSLError", "SSL", "HTTPSConnectionPool", "Max retries exceeded"]):
                    yield self.create_text_message(f"网络连接超时：\n\n{error_msg}\n\n这通常是由于以下原因：\n1. 历史数据量较大，需要较长时间获取\n2. 网络连接不稳定或SSL握手失败\n3. 数据源服务器响应较慢\n\n建议：\n1. 稍后重试（数据源可能暂时繁忙）\n2. 检查网络连接稳定性\n3. 尝试缩短日期范围或使用其他接口")
                    yield self.create_json_message({
                        "error": "ssl_timeout_error",
                        "message": "SSL连接超时，历史数据获取失败",
                        "details": error_msg,
                        "suggestion": "稍后重试或缩短日期范围"
                    })
                    return
                else:
                    # 使用统一的错误处理机制 - 从原工具迁移
                    yield from handle_akshare_error(e, self, f"股票代码: {symbol}, 接口: {interface}, 周期: {period}, 日期范围: {start_date}-{end_date}", str(timeout))
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
            logging.error(f"GetStockHistoricalQuotesTool error: {e}")
            text, payload = build_error_payload(e)
            yield self.create_text_message(text)
            yield self.create_json_message(payload)
            return

