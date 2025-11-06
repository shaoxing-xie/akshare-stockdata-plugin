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
    validate_stock_symbol,
    validate_date_format
)


class GetCompanyDisclosureTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetCompanyDisclosureTool received parameters: {tool_parameters}")

            interface = tool_parameters.get("interface", "")
            symbol = tool_parameters.get("symbol", "")
            start_date = tool_parameters.get("start_date", "")
            end_date = tool_parameters.get("end_date", "")
            market = tool_parameters.get("market", "沪深京")
            category = tool_parameters.get("category", "")
            keyword = tool_parameters.get("keyword", "")
            logging.info(f"Interface: {interface}, Symbol: {symbol}, Start Date: {start_date}, End Date: {end_date}, Market: {market}, Category: {category}, Keyword: {keyword}")

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

        # 定义接口配置
        interface_configs = {
            "stock_zh_a_disclosure_report_cninfo": {
                "fn": ak.stock_zh_a_disclosure_report_cninfo,
                "requires_symbol": True,
                "requires_date_range": True,
                "requires_market": True,
                "requires_category": True,
                "date_format": "YYYYMMDD",
                "description": "巨潮资讯-首页-公告查询-信息披露公告-沪深京"
            },
            "stock_zh_a_disclosure_relation_cninfo": {
                "fn": ak.stock_zh_a_disclosure_relation_cninfo,
                "requires_symbol": True,
                "requires_date_range": True,
                "requires_market": True,
                "requires_category": False,
                "date_format": "YYYYMMDD",
                "description": "巨潮资讯-首页-公告查询-信息披露调研-沪深京"
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
                    yield self.create_text_message(f"错误：'{config['description']}'接口需要 'start_date' 和 'end_date' 参数。请提供日期格式如 '20230618' 和 '20231219'。")
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

            # 检查市场参数要求
            if config.get("requires_market", False):
                if not market:
                    yield self.create_text_message(f"错误：'{config['description']}'接口需要 'market' 参数。请选择市场类型（如'沪深京'）。")
                    yield self.create_json_message({"error": "market_required", "message": f"{interface} requires 'market' parameter"})
                    return

            # 类别参数是可选的（仅信息披露公告接口需要）
            # category参数在信息披露公告接口中是可选的，所以不强制检查

            # 网络参数
            retries = int(tool_parameters.get("retries", 5))
            timeout_param = tool_parameters.get("timeout")
            timeout = float(timeout_param) if timeout_param is not None else None
            logging.info(f"Network params - retries: {retries}, timeout: {timeout}")

            # 构建调用参数
            call_params = {}

            # 处理股票代码参数（巨潮资讯接口需要原始格式，去掉前缀）
            processed_symbol = self._process_symbol_format(symbol, interface)
            call_params["symbol"] = processed_symbol

            # 处理日期范围参数
            if config.get("requires_date_range", False) and start_date and end_date:
                call_params["start_date"] = start_date
                call_params["end_date"] = end_date

            # 处理市场参数
            if config.get("requires_market", False) and market:
                call_params["market"] = market

            # 处理类别参数（信息披露公告接口）
            if config.get("requires_category", False) and category:
                call_params["category"] = category

            # 处理关键词参数（信息披露公告接口，可选）
            if interface == "stock_zh_a_disclosure_report_cninfo" and keyword:
                call_params["keyword"] = keyword

            logging.info(f"Call params: {call_params}")
            logging.info(f"Function: {config['fn']}")
            logging.info(f"Interface: {interface}, Symbol: {symbol}, Processed Symbol: {processed_symbol}, Start Date: {start_date}, End Date: {end_date}, Market: {market}, Category: {category if config.get('requires_category') else 'N/A'}")

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
                        context += f", 股票代码: {symbol}"
                    if start_date:
                        context += f", 开始日期: {start_date}"
                    if end_date:
                        context += f", 结束日期: {end_date}"
                    if market:
                        context += f", 市场: {market}"
                    if category:
                        context += f", 类别: {category}"
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
            logging.error(f"GetCompanyDisclosureTool error: {e}")
            text, payload = build_error_payload(e)
            yield self.create_text_message(text)
            yield self.create_json_message(payload)
            return

    def _process_symbol_format(self, symbol: str, interface: str) -> str:
        """处理股票代码格式，根据接口要求进行转换"""
        if not symbol:
            return symbol

        # 巨潮资讯接口需要原始股票代码格式（去掉前缀）
        if interface in ["stock_zh_a_disclosure_report_cninfo", "stock_zh_a_disclosure_relation_cninfo"]:
            # 如果带前缀，去掉前缀
            if symbol.upper().startswith('SH') or symbol.upper().startswith('SZ'):
                return symbol[2:]
            return symbol

        return symbol

