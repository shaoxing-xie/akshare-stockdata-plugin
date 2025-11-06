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


class GetBlockTradingTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetBlockTradingTool received parameters: {tool_parameters}")

            interface = tool_parameters.get("interface", "")
            start_date = tool_parameters.get("start_date", "")
            end_date = tool_parameters.get("end_date", "")
            security_type = tool_parameters.get("security_type", "")
            period = tool_parameters.get("period", "")
            period_short = tool_parameters.get("period_short", "")
            logging.info(f"Interface: {interface}, Start Date: {start_date}, End Date: {end_date}, Security Type: {security_type}, Period: {period}, Period Short: {period_short}")

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
            "stock_dzjy_sctj": {
                "fn": ak.stock_dzjy_sctj,
                "requires_date_range": False,
                "requires_security_type": False,
                "requires_period": False,
                "requires_period_short": False,
                "description": "东方财富网-数据中心-大宗交易-市场统计"
            },
            "stock_dzjy_mrmx": {
                "fn": ak.stock_dzjy_mrmx,
                "requires_date_range": True,
                "requires_security_type": True,
                "requires_period": False,
                "requires_period_short": False,
                "date_format": "YYYYMMDD",
                "description": "东方财富网-数据中心-大宗交易-每日明细"
            },
            "stock_dzjy_mrtj": {
                "fn": ak.stock_dzjy_mrtj,
                "requires_date_range": True,
                "requires_security_type": False,
                "requires_period": False,
                "requires_period_short": False,
                "date_format": "YYYYMMDD",
                "description": "东方财富网-数据中心-大宗交易-每日统计"
            },
            "stock_dzjy_hygtj": {
                "fn": ak.stock_dzjy_hygtj,
                "requires_date_range": False,
                "requires_security_type": False,
                "requires_period": True,
                "requires_period_short": False,
                "description": "东方财富网-数据中心-大宗交易-活跃 A 股统计"
            },
            "stock_dzjy_hyyybtj": {
                "fn": ak.stock_dzjy_hyyybtj,
                "requires_date_range": False,
                "requires_security_type": False,
                "requires_period": False,
                "requires_period_short": True,
                "description": "东方财富网-数据中心-大宗交易-活跃营业部统计"
            },
            "stock_dzjy_yybph": {
                "fn": ak.stock_dzjy_yybph,
                "requires_date_range": False,
                "requires_security_type": False,
                "requires_period": True,
                "requires_period_short": False,
                "description": "东方财富网-数据中心-大宗交易-营业部排行"
            }
        }

        # 获取接口配置
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"未知的接口: {interface}")
            yield self.create_json_message({"error": f"unknown interface: {interface}"})
            return

        try:
            # 检查日期范围参数要求
            if config.get("requires_date_range", False):
                if not start_date or not end_date:
                    yield self.create_text_message(f"错误：'{config['description']}'接口需要 'start_date' 和 'end_date' 参数。请提供日期格式如 '20220104' 和 '20220105'。")
                    yield self.create_json_message({"error": "date_range_required", "message": f"{interface} requires 'start_date' and 'end_date' parameters"})
                    return

                # 验证日期格式
                date_format = config.get("date_format", "YYYYMMDD")
                validation_result = None
                for result in validate_date_format(start_date, date_format, self):
                    if isinstance(result, bool):
                        validation_result = result
                    else:
                        yield result
                if validation_result is False:
                    return

                validation_result = None
                for result in validate_date_format(end_date, date_format, self):
                    if isinstance(result, bool):
                        validation_result = result
                    else:
                        yield result
                if validation_result is False:
                    return

            # 检查证券类型参数要求
            if config.get("requires_security_type", False):
                if not security_type:
                    yield self.create_text_message(f"错误：'{config['description']}'接口需要 'security_type' 参数。请选择证券类型（如'A股'）。")
                    yield self.create_json_message({"error": "security_type_required", "message": f"{interface} requires 'security_type' parameter"})
                    return

            # 检查统计周期参数要求（长周期）
            if config.get("requires_period", False):
                if not period:
                    yield self.create_text_message(f"错误：'{config['description']}'接口需要 'period' 参数。请选择统计周期（如'近一月'）。")
                    yield self.create_json_message({"error": "period_required", "message": f"{interface} requires 'period' parameter"})
                    return

            # 检查统计周期参数要求（短周期）
            if config.get("requires_period_short", False):
                if not period_short:
                    yield self.create_text_message(f"错误：'{config['description']}'接口需要 'period_short' 参数。请选择统计周期（如'近3日'）。")
                    yield self.create_json_message({"error": "period_short_required", "message": f"{interface} requires 'period_short' parameter"})
                    return

            # 网络参数
            retries = int(tool_parameters.get("retries", 5))
            timeout_param = tool_parameters.get("timeout")
            timeout = float(timeout_param) if timeout_param is not None else None
            logging.info(f"Network params - retries: {retries}, timeout: {timeout}")

            # 构建调用参数
            call_params = {}

            # 处理日期范围参数
            if config.get("requires_date_range", False) and start_date and end_date:
                call_params["start_date"] = start_date
                call_params["end_date"] = end_date

            # 处理证券类型参数
            if config.get("requires_security_type", False) and security_type:
                call_params["symbol"] = security_type

            # 处理统计周期参数（长周期）
            if config.get("requires_period", False) and period:
                call_params["symbol"] = period

            # 处理统计周期参数（短周期）
            if config.get("requires_period_short", False) and period_short:
                call_params["symbol"] = period_short

            logging.info(f"Call params: {call_params}")
            logging.info(f"Function: {config['fn']}")
            logging.info(f"Interface: {interface}, Start Date: {start_date if config.get('requires_date_range') else 'N/A'}, End Date: {end_date if config.get('requires_date_range') else 'N/A'}, Security Type: {security_type if config.get('requires_security_type') else 'N/A'}, Period: {period if config.get('requires_period') else 'N/A'}, Period Short: {period_short if config.get('requires_period_short') else 'N/A'}")

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
                    if start_date:
                        context += f", 开始日期: {start_date}"
                    if end_date:
                        context += f", 结束日期: {end_date}"
                    if security_type:
                        context += f", 证券类型: {security_type}"
                    if period:
                        context += f", 统计周期: {period}"
                    if period_short:
                        context += f", 统计周期: {period_short}"
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
            logging.error(f"GetBlockTradingTool error: {e}")
            text, payload = build_error_payload(e)
            yield self.create_text_message(text)
            yield self.create_json_message(payload)
            return

