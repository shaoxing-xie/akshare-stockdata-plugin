from collections.abc import Generator
from typing import Any
import pandas as pd

import akshare as ak
from provider.akshare_stockdata import safe_ak_call, build_error_payload
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .common_utils import process_dataframe_output, process_other_output, handle_empty_result, validate_date_format, handle_akshare_error


class GetExchangeMarketOverviewTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetExchangeMarketOverviewTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            logging.info(f"Interface: {interface}")
            
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
            "stock_sse_summary": {
                "fn": ak.stock_sse_summary,
                "requires_date": False,
                "date_format": None,
                "description": "上交所股票数据总貌-最近交易日"
            },
            "stock_szse_summary": {
                "fn": ak.stock_szse_summary,
                "requires_date": True,
                "date_format": "YYYYMMDD",
                "description": "深交所证券类别统计-指定交易日"
            },
            "stock_sse_deal_daily": {
                "fn": ak.stock_sse_deal_daily,
                "requires_date": True,
                "date_format": "YYYYMMDD",
                "description": "上交所每日股票概况-指定交易日"
            }
        }
        
        # 获取接口配置
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"未知的接口: {interface}")
            yield self.create_json_message({"error": f"unknown interface: {interface}"})
            return
        
        try:
            # 检查日期参数要求
            date = tool_parameters.get("date", "")
            if config["requires_date"] and not date:
                yield self.create_text_message(f"错误：'{config['description']}'接口需要 'date' 参数。请提供日期格式如 '20240630'。")
                yield self.create_json_message({"error": "date_required", "message": f"{interface} requires 'date' parameter"})
                return
            
            # 验证日期格式
            if config["requires_date"] and date:
                logging.info(f"Validating date format: {date} with format {config['date_format']}")
                validation_result = None
                for result in validate_date_format(date, config["date_format"], self):
                    if isinstance(result, bool):
                        validation_result = result
                    else:
                        yield result
                if validation_result is False:
                    logging.error(f"Date validation failed for {date}")
                    return
                logging.info(f"Date validation passed for {date}")
            
            # 网络参数 - 统一处理逻辑（从原工具迁移）
            retries = int(tool_parameters.get("retries", 5))
            timeout_param = tool_parameters.get("timeout")  # 让子进程根据接口类型自动决定超时时间
            timeout = float(timeout_param) if timeout_param is not None else None
            logging.info(f"Network params - retries: {retries}, timeout: {timeout} (auto-determined by interface type)")
            
            # 构建调用参数（从原工具迁移）
            call_params = {}
            if config["requires_date"] and date:
                call_params["date"] = date
            
            logging.info(f"Call params: {call_params}")
            logging.info(f"Function: {config['fn']}")
            logging.info(f"Interface: {interface}, Date: {date}")
            
            # 调用AKShare接口 - timeout现在仅用于子进程超时控制（从原工具迁移）
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
                logging.error(f"safe_ak_call failed for {interface} with date {date}: {e}")
                # 检查是否是SSL连接错误（从原工具迁移）
                error_msg = str(e)
                if any(keyword in error_msg for keyword in ["SSLError", "SSL", "HTTPSConnectionPool", "Max retries exceeded"]):
                    yield self.create_text_message(f"网络连接超时：\n\n{error_msg}\n\n这通常是由于以下原因：\n1. 市场数据量较大，需要较长时间获取\n2. 网络连接不稳定或SSL握手失败\n3. 数据源服务器响应较慢\n\n建议：\n1. 稍后重试（数据源可能暂时繁忙）\n2. 检查网络连接稳定性\n3. 尝试其他市场数据接口")
                    yield self.create_json_message({
                        "error": "ssl_timeout_error",
                        "message": "SSL连接超时，市场数据获取失败",
                        "details": error_msg,
                        "suggestion": "稍后重试或尝试其他接口"
                    })
                    return
                else:
                    # 使用统一的错误处理机制（从原工具迁移）
                    yield from handle_akshare_error(e, self, f"接口: {interface}, 日期: {date}", str(timeout))
                    return
            
            # 处理结果
            if result is None:
                yield from handle_empty_result(self)
                return
            
            # 检查是否为空
            if hasattr(result, 'empty') and result.empty:
                yield from handle_empty_result(self)
                return
            
            # 输出处理
            if isinstance(result, pd.DataFrame):
                yield from process_dataframe_output(result, self)
            else:
                yield from process_other_output(result, self)
                
        except Exception as e:
            import logging
            logging.error(f"GetExchangeMarketOverviewTool error: {e}")
            text, payload = build_error_payload(e)
            yield self.create_text_message(text)
            yield self.create_json_message(payload)
            return

