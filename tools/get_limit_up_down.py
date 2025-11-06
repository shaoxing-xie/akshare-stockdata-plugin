from collections.abc import Generator
from typing import Any
import pandas as pd

import akshare as ak
from provider.akshare_stockdata import safe_ak_call, build_error_payload
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .common_utils import (
    process_dataframe_output,
    process_other_output,
    handle_empty_result,
    handle_akshare_error,
    validate_date_format
)


class GetLimitUpDownTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetLimitUpDownTool received parameters: {tool_parameters}")

            interface = tool_parameters.get("interface", "")
            date = tool_parameters.get("date", "")
            logging.info(f"Interface: {interface}, Date: {date}")

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
            "stock_zt_pool_em": {
                "fn": ak.stock_zt_pool_em,
                "requires_date": True,
                "date_format": "YYYYMMDD",
                "description": "涨停股池"
            },
            "stock_zt_pool_previous_em": {
                "fn": ak.stock_zt_pool_previous_em,
                "requires_date": True,
                "date_format": "YYYYMMDD",
                "description": "昨日涨停股池"
            },
            "stock_zt_pool_strong_em": {
                "fn": ak.stock_zt_pool_strong_em,
                "requires_date": True,
                "date_format": "YYYYMMDD",
                "description": "强势股池"
            },
            "stock_zt_pool_sub_new_em": {
                "fn": ak.stock_zt_pool_sub_new_em,
                "requires_date": True,
                "date_format": "YYYYMMDD",
                "description": "次新股池"
            },
            "stock_zt_pool_zbgc_em": {
                "fn": ak.stock_zt_pool_zbgc_em,
                "requires_date": True,
                "date_format": "YYYYMMDD",
                "description": "炸板股池"
            },
            "stock_zt_pool_dtgc_em": {
                "fn": ak.stock_zt_pool_dtgc_em,
                "requires_date": True,
                "date_format": "YYYYMMDD",
                "description": "跌停股池"
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
            if config.get("requires_date", False):
                if not date:
                    yield self.create_text_message(f"错误：'{config['description']}'接口需要 'date' 参数。请提供日期格式如 '20241008'。")
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

            # 网络参数
            retries = int(tool_parameters.get("retries", 5))
            timeout_param = tool_parameters.get("timeout")
            timeout = float(timeout_param) if timeout_param is not None else None
            logging.info(f"Network params - retries: {retries}, timeout: {timeout}")

            # 构建调用参数
            call_params = {}

            # 处理日期参数
            if config.get("requires_date", False) and date:
                call_params["date"] = date

            logging.info(f"Call params: {call_params}")
            logging.info(f"Function: {config['fn']}")
            logging.info(f"Interface: {interface}, Date: {date if config.get('requires_date') else 'N/A'}")

            # 调用AKShare接口
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
                logging.error(f"safe_ak_call failed for {interface}: {e}")
                error_msg = str(e)
                if any(keyword in error_msg for keyword in ["SSLError", "SSL", "HTTPSConnectionPool", "Max retries exceeded"]):
                    yield self.create_text_message(f"网络连接超时：\n\n{error_msg}\n\n这通常是由于以下原因：\n1. 数据量较大，需要较长时间获取\n2. 网络连接不稳定或SSL握手失败\n3. 数据源服务器响应较慢\n\n建议：\n1. 稍后重试（数据源可能暂时繁忙）\n2. 检查网络连接稳定性\n3. 尝试其他接口")
                    yield self.create_json_message({
                        "error": "ssl_timeout_error",
                        "message": "SSL连接超时，数据获取失败",
                        "details": error_msg,
                        "suggestion": "稍后重试或尝试其他接口"
                    })
                    return
                else:
                    context = f"接口: {interface}"
                    if date:
                        context += f", 日期: {date}"
                    yield from handle_akshare_error(e, self, context, str(timeout))
                    return

            # 处理结果
            if result is None:
                yield from handle_empty_result(self)
                return

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
            logging.error(f"GetLimitUpDownTool error: {e}")
            text, payload = build_error_payload(e)
            yield self.create_text_message(text)
            yield self.create_json_message(payload)
            return

