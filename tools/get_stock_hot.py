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
    handle_akshare_error
)


class GetStockHotTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetStockHotTool received parameters: {tool_parameters}")

            interface = tool_parameters.get("interface", "")
            symbol = tool_parameters.get("symbol", "")
            logging.info(f"Interface: {interface}, Symbol: {symbol}")

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
            "stock_hot_follow_xq": {
                "fn": ak.stock_hot_follow_xq,
                "requires_symbol": True,
                "valid_symbols": ["最热门", "本周新增"],
                "description": "雪球-关注排行榜"
            },
            "stock_hot_tweet_xq": {
                "fn": ak.stock_hot_tweet_xq,
                "requires_symbol": True,
                "valid_symbols": ["最热门", "本周新增"],
                "description": "雪球-讨论排行榜"
            },
            "stock_hot_deal_xq": {
                "fn": ak.stock_hot_deal_xq,
                "requires_symbol": True,
                "valid_symbols": ["最热门", "本周新增"],
                "description": "雪球-交易排行榜"
            },
            "stock_hot_rank_em": {
                "fn": ak.stock_hot_rank_em,
                "requires_symbol": False,
                "valid_symbols": None,
                "description": "东方财富-人气榜-A股"
            },
            "stock_hot_up_em": {
                "fn": ak.stock_hot_up_em,
                "requires_symbol": False,
                "valid_symbols": None,
                "description": "东方财富-飙升榜-A股"
            },
            "stock_hk_hot_rank_em": {
                "fn": ak.stock_hk_hot_rank_em,
                "requires_symbol": False,
                "valid_symbols": None,
                "description": "东方财富-人气榜-港股"
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
                    yield self.create_text_message(f"错误：'{config['description']}'接口需要 'symbol' 参数（排行类别）。请选择排行类别：最热门、本周新增。")
                    yield self.create_json_message({"error": "symbol_required", "message": f"{interface} requires 'symbol' parameter (ranking category)"})
                    return

                # 验证symbol参数值
                valid_symbols = config.get("valid_symbols")
                if valid_symbols and symbol not in valid_symbols:
                    valid_options = "、".join(valid_symbols)
                    yield self.create_text_message(f"错误：'{config['description']}'接口的 'symbol' 参数值 '{symbol}' 无效。\n\n有效选项：{valid_options}\n\n请选择正确的排行类别：\n- 最热门：显示最热门的股票\n- 本周新增：显示本周新增关注的股票")
                    yield self.create_json_message({
                        "error": "invalid_symbol_value",
                        "message": f"{interface} received invalid symbol value: {symbol}",
                        "valid_options": valid_symbols
                    })
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

            logging.info(f"Call params: {call_params}")
            logging.info(f"Function: {config['fn']}")
            logging.info(f"Interface: {interface}, Symbol: {symbol if config.get('requires_symbol') else 'N/A'}")

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
                        context += f", 排行类别: {symbol}"
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
            logging.error(f"GetStockHotTool error: {e}")
            text, payload = build_error_payload(e)
            yield self.create_text_message(text)
            yield self.create_json_message(payload)
            return

