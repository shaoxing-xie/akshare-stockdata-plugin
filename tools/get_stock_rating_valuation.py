from collections.abc import Generator
from typing import Any
import pandas as pd

import akshare as ak
from provider.akshare_stockdata import safe_ak_call, build_error_payload
from provider.akshare_registry import get_interface_config
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .common_utils import (
    process_dataframe_output, 
    process_other_output, 
    handle_empty_result, 
    handle_akshare_error, 
    validate_stock_symbol,
    validate_date_format
)


class GetStockRatingValuationTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetStockRatingValuationTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            symbol = tool_parameters.get("symbol", "")
            date = tool_parameters.get("date", "")
            logging.info(f"Interface: {interface}, Symbol: {symbol}, Date: {date}")
            
            if not interface:
                yield self.create_text_message("请选择要调用的接口")
                yield self.create_json_message({"error": "interface required", "received_params": tool_parameters})
                return
        except Exception as e:
            logging.error(f"Error in _invoke start: {e}")
            yield self.create_text_message(f"参数处理错误: {e}")
            yield self.create_json_message({"error": f"parameter processing error: {e}"})
            return
        
        # 定义接口配置
        interface_configs = {
            "stock_institute_recommend_detail": {
                "fn": ak.stock_institute_recommend_detail,
                "requires_symbol": True,
                "requires_date": False,
                "description": "新浪财经-机构推荐池-股票评级记录-指定股票"
            },
            "stock_value_em": {
                "fn": ak.stock_value_em,
                "requires_symbol": True,
                "requires_date": False,
                "description": "东方财富-估值分析-指定股票"
            },
            "stock_rank_forecast_cninfo": {
                "fn": ak.stock_rank_forecast_cninfo,
                "requires_symbol": False,
                "requires_date": True,
                "date_format": "YYYYMMDD",
                "description": "巨潮资讯-投资评级-指定日期"
            }
        }
        
        # 获取接口配置
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"未知的接口: {interface}")
            yield self.create_json_message({"error": f"unknown interface: {interface}"})
            return
        
        try:
            # 检查股票代码参数要求
            if config.get("requires_symbol", False):
                if not symbol:
                    yield self.create_text_message(f"错误：'{config['description']}'接口需要 'symbol' 参数。请提供股票代码（如'600519'）。")
                    yield self.create_json_message({"error": "symbol_required", "message": f"{interface} requires 'symbol' parameter"})
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
            
            # 检查日期参数要求
            if config.get("requires_date", False):
                if not date:
                    yield self.create_text_message(f"错误：'{config['description']}'接口需要 'date' 参数。请提供日期格式如 '20240101'。")
                    yield self.create_json_message({"error": "date_required", "message": f"{interface} requires 'date' parameter"})
                    return
                
                # 验证日期格式
                date_format = config.get("date_format", "YYYYMMDD")
                validation_result = None
                for result in validate_date_format(date, date_format, self):
                    if isinstance(result, bool):
                        validation_result = result
                    else:
                        yield result
                if validation_result is False:
                    return
            # 网络参数 - 统一处理逻辑 - 从原工具迁移
            retries = int(tool_parameters.get("retries", 5))
            timeout_param = tool_parameters.get("timeout")
            timeout = float(timeout_param) if timeout_param is not None else None
            logging.info(f"Network params - retries: {retries}, timeout: {timeout} (auto-determined by interface type)")
            
            # 构建调用参数
            call_params = {}
            
            # 处理股票代码参数
            if config.get("requires_symbol", False) and symbol:
                processed_symbol = self._process_symbol_format(symbol, interface)
                call_params["symbol"] = processed_symbol
            
            # 处理日期参数
            if config.get("requires_date", False) and date:
                call_params["date"] = date
            
            logging.info(f"Call params: {call_params}")
            logging.info(f"Function: {config['fn']}")
            logging.info(f"Interface: {interface}, Symbol: {symbol if config.get('requires_symbol') else 'N/A'}, Date: {date if config.get('requires_date') else 'N/A'}")
            
            # 调用AKShare接口 - 从原工具迁移
            try:
                logging.info(f"About to call safe_ak_call with {call_params}")
                result = safe_ak_call(
                    config["fn"],
                    retries=retries,
                    timeout=timeout,
                    **call_params
                )
                logging.info(f"safe_ak_call completed successfully for {interface}")
            except Exception as e:
                logging.error(f"safe_ak_call failed for {interface} with symbol {symbol}: {e}")
                error_msg = str(e)
                if any(keyword in error_msg for keyword in ["SSLError", "SSL", "HTTPSConnectionPool", "Max retries exceeded"]):
                    yield self.create_text_message(f"网络连接超时：\n\n{error_msg}\n\n这通常是由于以下原因：\n1. 个股数据量较大，需要较长时间获取\n2. 网络连接不稳定或SSL握手失败\n3. 数据源服务器响应较慢\n\n建议：\n1. 稍后重试（数据源可能暂时繁忙）\n2. 检查网络连接稳定性\n3. 尝试其他个股信息接口")
                    yield self.create_json_message({
                        "error": "ssl_timeout_error",
                        "message": "SSL连接超时，个股信息获取失败",
                        "details": error_msg,
                        "suggestion": "稍后重试或尝试其他接口"
                    })
                    return
                else:
                    context = f"接口: {interface}"
                    if symbol:
                        context += f", 股票代码: {symbol}"
                    if date:
                        context += f", 日期: {date}"
                    yield from handle_akshare_error(e, self, context, str(timeout))
                    return
            
            # 处理结果 - 从原工具迁移
            if result is None:
                yield from handle_empty_result(self)
                return
            
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
            logging.error(f"GetStockRatingValuationTool error: {e}")
            text, payload = build_error_payload(e)
            yield self.create_text_message(text)
            yield self.create_json_message(payload)
            return
    
    def _process_symbol_format(self, symbol: str, interface: str) -> str:
        """处理股票代码格式，根据接口要求进行转换 - 从原工具迁移"""
        if not symbol:
            return symbol
        
        # 需要带市场前缀的接口
        prefix_required_interfaces = []
        
        # 需要小写市场前缀的接口
        lowercase_prefix_interfaces = []
        
        # 处理需要小写市场前缀的接口
        if interface in lowercase_prefix_interfaces and not any(symbol.lower().startswith(prefix) for prefix in ['sh', 'sz', 'hk']):
            if symbol.isdigit() and len(symbol) == 6:
                if symbol.startswith(('60', '68')):
                    return f"sh{symbol}"
                elif symbol.startswith(('00', '30')):
                    return f"sz{symbol}"
        
        # 如果接口需要前缀且当前代码没有前缀
        if interface in prefix_required_interfaces and not any(symbol.upper().startswith(prefix) for prefix in ['SH', 'SZ', 'HK']):
            if symbol.isdigit() and len(symbol) == 6:
                if symbol.startswith(('60', '68')):
                    return f"SH{symbol}"
                elif symbol.startswith(('00', '30')):
                    return f"SZ{symbol}"
        
        return symbol

