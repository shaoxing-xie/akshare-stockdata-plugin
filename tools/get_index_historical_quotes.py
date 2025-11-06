from collections.abc import Generator
from typing import Any
import pandas as pd

import akshare as ak
from provider.akshare_stockdata import safe_ak_call
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .common_utils import (
    process_dataframe_output, 
    process_other_output, 
    handle_empty_result, 
    handle_akshare_error
)


class GetIndexHistoricalQuotesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetIndexHistoricalQuotesTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            symbol = tool_parameters.get("symbol", "")
            period = tool_parameters.get("period", "daily")
            start_date = tool_parameters.get("start_date", "")
            end_date = tool_parameters.get("end_date", "")
            retries = int(tool_parameters.get("retries", 5))
            timeout = float(tool_parameters.get("timeout", 900))
            
            logging.info(f"Interface: {interface}, Symbol: {symbol}, Period: {period}, StartDate: {start_date}, EndDate: {end_date}, Retries: {retries}, Timeout: {timeout}")
            
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
            "stock_zh_index_daily": {
                "fn": ak.stock_zh_index_daily,
                "requires_symbol": True,
                "requires_prefix": True,
                "description": "新浪财经-A股指数-历史行情数据-指定指数"
            },
            "stock_zh_index_daily_tx": {
                "fn": ak.stock_zh_index_daily_tx,
                "requires_symbol": True,
                "requires_prefix": True,
                "description": "腾讯-A股指数-历史行情数据-指定指数"
            },
            "stock_zh_index_daily_em": {
                "fn": ak.stock_zh_index_daily_em,
                "requires_symbol": True,
                "requires_prefix": True,
                "requires_date_range": True,
                "description": "东方财富-A股指数-历史行情数据-指定指数、日期范围"
            },
            "index_zh_a_hist": {
                "fn": ak.index_zh_a_hist,
                "requires_symbol": True,
                "requires_digits_only": True,
                "requires_period": True,
                "requires_date_range": True,
                "description": "东方财富-A股指数-历史行情数据-通用-指定指数、周期、日期范围"
            },
        }
        
        # 获取接口配置
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"不支持的接口: {interface}")
            yield self.create_json_message({"error": f"unsupported interface: {interface}"})
            return
        
        try:
            # 构建调用参数
            call_params = {}
            
            # 处理指数代码
            if config.get("requires_symbol"):
                if not symbol:
                    yield self.create_text_message("此接口需要指数代码参数")
                    yield self.create_json_message({"error": "symbol required for this interface"})
                    return
                
                if config.get("requires_prefix"):
                    # 需要带市场前缀的格式
                    if not (symbol.lower().startswith('sh') or symbol.lower().startswith('sz')):
                        yield self.create_text_message(f"指数代码格式错误，需要带市场标识（如sh000001、sz399552）")
                        yield self.create_json_message({"error": "Invalid symbol format, requires prefix"})
                        return
                    call_params["symbol"] = symbol.lower()
                elif config.get("requires_digits_only"):
                    # 需要纯数字格式
                    symbol_digits = "".join(ch for ch in str(symbol) if ch.isdigit())
                    if not symbol_digits or len(symbol_digits) != 6:
                        yield self.create_text_message(f"指数代码格式错误，需要6位纯数字格式（如000001、399006）")
                        yield self.create_json_message({"error": "Invalid symbol format, requires 6 digits"})
                        return
                    call_params["symbol"] = symbol_digits
            
            # 处理周期参数
            if config.get("requires_period"):
                call_params["period"] = period
            
            # 处理日期范围
            if config.get("requires_date_range"):
                if not start_date or not end_date:
                    yield self.create_text_message("此接口需要日期范围（开始日期和结束日期）")
                    yield self.create_json_message({"error": "date range required for this interface"})
                    return
                call_params["start_date"] = start_date
                call_params["end_date"] = end_date
            
            # 使用接口特定的超时时间
            interface_timeout = config.get("timeout", timeout)
            
            # 调用接口
            result = safe_ak_call(
                config["fn"],
                retries=retries,
                timeout=interface_timeout,
                **call_params
            )
            
            if result is None:
                yield self.create_text_message("接口调用失败，未返回数据")
                yield self.create_json_message({"error": "interface call failed, no data returned"})
                return
            
            # 处理结果
            if isinstance(result, pd.DataFrame):
                if result.empty:
                    yield self.create_text_message("接口返回空数据")
                    yield self.create_json_message({"data": [], "message": "empty result"})
                    return
                
                # 处理DataFrame输出
                yield from process_dataframe_output(result, self)
            else:
                # 处理其他类型输出
                yield from process_other_output(result, self)
                
        except Exception as e:
            yield from handle_akshare_error(e, self, f"接口: {interface}")

