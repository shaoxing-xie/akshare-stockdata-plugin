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


class GetIndustryBoardTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetIndustryBoardTool received parameters: {tool_parameters}")

            interface = tool_parameters.get("interface", "")
            symbol = tool_parameters.get("symbol", "")
            start_date = tool_parameters.get("start_date", "")
            end_date = tool_parameters.get("end_date", "")
            period = tool_parameters.get("period", "")
            adjust = tool_parameters.get("adjust", "")
            minute_period = tool_parameters.get("minute_period", "")
            logging.info(f"Interface: {interface}, Symbol: {symbol}, Start Date: {start_date}, End Date: {end_date}, Period: {period}, Adjust: {adjust}, Minute Period: {minute_period}")

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
            "stock_board_industry_summary_ths": {
                "fn": ak.stock_board_industry_summary_ths,
                "requires_symbol": False,
                "requires_date_range": False,
                "requires_period": False,
                "requires_adjust": False,
                "requires_minute_period": False,
                "description": "同花顺-同花顺行业一览表"
            },
            "stock_board_industry_index_ths": {
                "fn": ak.stock_board_industry_index_ths,
                "requires_symbol": True,
                "requires_date_range": True,
                "requires_period": False,
                "requires_adjust": False,
                "requires_minute_period": False,
                "date_format": "YYYYMMDD",
                "description": "同花顺-行业板块-指数日频率数据-指定行业板块、日期范围"
            },
            "stock_board_industry_name_em": {
                "fn": ak.stock_board_industry_name_em,
                "requires_symbol": False,
                "requires_date_range": False,
                "requires_period": False,
                "requires_adjust": False,
                "requires_minute_period": False,
                "description": "东方财富-行业板块"
            },
            "stock_board_industry_spot_em": {
                "fn": ak.stock_board_industry_spot_em,
                "requires_symbol": True,
                "requires_date_range": False,
                "requires_period": False,
                "requires_adjust": False,
                "requires_minute_period": False,
                "description": "东方财富-行业板块-实时行情-指定行业名称"
            },
            "stock_board_industry_cons_em": {
                "fn": ak.stock_board_industry_cons_em,
                "requires_symbol": True,
                "requires_date_range": False,
                "requires_period": False,
                "requires_adjust": False,
                "requires_minute_period": False,
                "description": "东方财富-行业板块-板块成份-指定行业名称或板块代码"
            },
            "stock_board_industry_hist_em": {
                "fn": ak.stock_board_industry_hist_em,
                "requires_symbol": True,
                "requires_date_range": True,
                "requires_period": True,
                "requires_adjust": True,
                "requires_minute_period": False,
                "date_format": "YYYYMMDD",
                "description": "东方财富-行业板块-历史行情数据-指定行业名称、周期、日期范围和复权方式"
            },
            "stock_board_industry_hist_min_em": {
                "fn": ak.stock_board_industry_hist_min_em,
                "requires_symbol": True,
                "requires_date_range": False,
                "requires_period": False,
                "requires_adjust": False,
                "requires_minute_period": True,
                "description": "东方财富-行业板块-分时历史行情数据-指定行业名称和分时周期"
            }
        }

        # 获取接口配置
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"未知的接口: {interface}")
            yield self.create_json_message({"error": f"unknown interface: {interface}"})
            return

        try:
            # 检查symbol参数要求
            if config.get("requires_symbol", False):
                if not symbol:
                    yield self.create_text_message(f"错误：'{config['description']}'接口需要 'symbol' 参数（行业名称）。请提供行业名称，如'元件'、'小金属'、'煤炭行业'等。")
                    yield self.create_json_message({"error": "symbol_required", "message": f"{interface} requires 'symbol' parameter (industry name)"})
                    return

            # 检查日期范围参数要求
            if config.get("requires_date_range", False):
                if not start_date or not end_date:
                    yield self.create_text_message(f"错误：'{config['description']}'接口需要 'start_date' 和 'end_date' 参数。请提供日期格式如 '20240101' 和 '20240718'。")
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

            # 检查周期参数要求
            if config.get("requires_period", False):
                if not period:
                    yield self.create_text_message(f"错误：'{config['description']}'接口需要 'period' 参数。请选择周期（如'日k'、'周k'、'月k'）。")
                    yield self.create_json_message({"error": "period_required", "message": f"{interface} requires 'period' parameter"})
                    return

            # 检查复权方式参数要求
            if config.get("requires_adjust", False):
                # adjust参数可以为空字符串（不复权），所以不需要强制检查
                pass

            # 检查分时周期参数要求
            if config.get("requires_minute_period", False):
                if not minute_period:
                    yield self.create_text_message(f"错误：'{config['description']}'接口需要 'minute_period' 参数。请选择分时周期（如'1'、'5'、'15'、'30'、'60'）。")
                    yield self.create_json_message({"error": "minute_period_required", "message": f"{interface} requires 'minute_period' parameter"})
                    return

            # 网络参数
            retries = int(tool_parameters.get("retries", 5))
            timeout_param = tool_parameters.get("timeout")
            timeout = float(timeout_param) if timeout_param is not None else None
            logging.info(f"Network params - retries: {retries}, timeout: {timeout}")

            # 构建调用参数
            call_params = {}

            # 处理symbol参数
            if config.get("requires_symbol", False) and symbol:
                call_params["symbol"] = symbol

            # 处理日期范围参数
            if config.get("requires_date_range", False) and start_date and end_date:
                call_params["start_date"] = start_date
                call_params["end_date"] = end_date

            # 处理周期参数
            if config.get("requires_period", False) and period:
                call_params["period"] = period

            # 处理复权方式参数
            if config.get("requires_adjust", False):
                # adjust参数可以为空字符串，需要显式传递
                # 如果传入的是"none"（用于表示空字符串），则转换为空字符串
                if adjust == "none":
                    call_params["adjust"] = ""
                else:
                    call_params["adjust"] = adjust if adjust is not None else ""

            # 处理分时周期参数
            if config.get("requires_minute_period", False) and minute_period:
                call_params["period"] = minute_period

            logging.info(f"Call params: {call_params}")
            logging.info(f"Function: {config['fn']}")
            logging.info(f"Interface: {interface}, Symbol: {symbol if config.get('requires_symbol') else 'N/A'}, Start Date: {start_date if config.get('requires_date_range') else 'N/A'}, End Date: {end_date if config.get('requires_date_range') else 'N/A'}, Period: {period if config.get('requires_period') else (minute_period if config.get('requires_minute_period') else 'N/A')}, Adjust: {adjust if config.get('requires_adjust') else 'N/A'}")

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
                    if symbol:
                        context += f", 行业名称: {symbol}"
                    if start_date:
                        context += f", 开始日期: {start_date}"
                    if end_date:
                        context += f", 结束日期: {end_date}"
                    if period:
                        context += f", 周期: {period}"
                    if minute_period:
                        context += f", 分时周期: {minute_period}"
                    if adjust:
                        context += f", 复权方式: {adjust}"
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
            logging.error(f"GetIndustryBoardTool error: {e}")
            text, payload = build_error_payload(e)
            yield self.create_text_message(text)
            yield self.create_json_message(payload)
            return

