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
    handle_akshare_error
)


class GetUsHistoricalQuotesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetUsHistoricalQuotesTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            symbol = tool_parameters.get("stock_code", "")  # 美股代码
            period = tool_parameters.get("period", "daily")  # 周期（历史行情类）
            start_date = tool_parameters.get("start_date", "20250101")
            end_date = tool_parameters.get("end_date", "20250915")
            adjust = tool_parameters.get("adjust", "none")
            retries = int(tool_parameters.get("retries", 5))
            timeout = float(tool_parameters.get("timeout", 600))
            
            logging.info(f"Interface: {interface}, Symbol: {symbol}, Period: {period}, StartDate: {start_date}, EndDate: {end_date}, Adjust: {adjust}, Retries: {retries}, Timeout: {timeout}")
            
            if not interface:
                yield self.create_text_message("请选择要调用的接口")
                yield self.create_json_message({"error": "interface required", "received_params": tool_parameters})
                return
                
        except Exception as e:
            logging.error(f"Error in _invoke start: {e}")
            yield self.create_text_message(f"参数处理错误: {e}")
            yield self.create_json_message({"error": f"parameter processing error: {e}"})
            return
        
        # 定义接口配置 - 完全按照原工具stock_us_data的实现
        interface_configs = {
            "stock_us_daily": {
                "fn": ak.stock_us_daily,
                "requires_symbol": True,
                "requires_adjust": True,
                "description": "新浪-美股-历史行情数据-指定股票代码、复权方式"
            },
            "stock_us_hist": {
                "fn": ak.stock_us_hist,
                "requires_symbol": True,
                "requires_period": True,
                "requires_date_range": True,
                "requires_adjust": True,
                "supports_timeout": False,
                "description": "美股-每日行情-指定股票代码、周期、日期范围、复权方式"
            },
            # 注意：stock_us_hist_min_em 接口已独立到工具 get_us_daily_minute_quotes
            # "stock_us_hist_min_em": {
            #     "fn": ak.stock_us_hist_min_em,
            #     "requires_symbol": True,
            #     "requires_period": False,  # 美股分时接口不需要period参数
            #     "requires_date_range": False,  # 美股分时接口不需要日期范围，自动返回最近5天
            #     "requires_adjust": False,
            #     "supports_timeout": False,
            #     "description": "美股-每日分时行情(自动最近5天)-指定股票代码"
            # },
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
            
            # 处理股票代码
            if config.get("requires_symbol"):
                if not symbol:
                    yield self.create_text_message("此接口需要美股代码参数")
                    yield self.create_json_message({"error": "symbol required for this interface"})
                    return
                
                # 美股代码格式转换 - 完全按照原工具stock_us_data的实现
                if symbol.startswith("US."):
                    # 去掉US前缀，如US.AAPL -> AAPL
                    symbol = symbol[3:]
                
                # 根据接口类型决定是否需要105.前缀
                # 只有历史数据接口需要105.前缀，新浪接口使用原始格式
                if interface == "stock_us_hist":
                    # 历史数据接口需要105.前缀
                    if symbol.startswith("105."):
                        symbol = symbol.upper()
                    else:
                        if symbol.isalpha() and len(symbol) <= 6:
                            symbol = f"105.{symbol.upper()}"
                        else:
                            symbol = symbol.upper()
                else:
                    # 新浪接口使用原始格式
                    symbol = symbol.upper()
                
                call_params["symbol"] = symbol
            
            # 处理周期参数
            if config.get("requires_period"):
                period_type = config.get("period_type", "")
                if period_type == "historical":
                    # 历史行情接口使用周期一
                    call_params["period"] = period
                elif period_type == "minute":
                    # 分时行情接口使用周期二
                    period2 = tool_parameters.get("period2", "5")
                    call_params["period"] = period2
            
            # 处理日期范围
            if config.get("requires_date_range"):
                call_params["start_date"] = start_date
                call_params["end_date"] = end_date
            
            # 处理复权方式
            if config.get("requires_adjust"):
                if adjust == "none":
                    call_params["adjust"] = ""  # "none" 对应空字符串，表示不复权
                elif adjust:
                    call_params["adjust"] = adjust
            
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

