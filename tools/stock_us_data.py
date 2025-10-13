from collections.abc import Generator
from typing import Any
import pandas as pd

import akshare as ak
from provider.akshare_stockdata import safe_ak_call, build_error_payload
from provider.akshare_registry import get_interface_config
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .common_utils import process_dataframe_output, process_other_output, handle_empty_result, handle_akshare_error


class StockUsDataTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"StockUsDataTool received parameters: {tool_parameters}")
            
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
        
        # 定义美股接口配置
        interface_configs = {
            # 美股实时行情接口
            "stock_us_spot_em": {
                "fn": ak.stock_us_spot_em,
                "description": "美股-实时行情"
            },
            "stock_us_spot": {
                "fn": ak.stock_us_spot,
                "description": "新浪-美股-实时行情(延15分钟)"
            },
            "stock_us_famous_spot_em": {
                "fn": ak.stock_us_famous_spot_em,
                "description": "知名美股的实时行情数据-指定类别"
            },
            # 美股历史行情接口
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
                "period_type": "historical",  # 历史行情类
                "requires_date_range": True,
                "requires_adjust": True,
                "supports_timeout": False,
                "description": "美股-每日行情-指定股票代码、周期、日期范围、复权方式"
            },
            "stock_us_hist_min_em": {
                "fn": ak.stock_us_hist_min_em,
                "requires_symbol": True,
                "requires_period": False,  # 美股分时接口不需要period参数
                "requires_date_range": False,  # 美股分时接口不需要日期范围，自动返回最近5天
                "requires_adjust": False,
                "supports_timeout": False,
                "description": "美股-每日分时行情(自动最近5天)-指定股票代码"
            },
            # 美股财务分析接口
            "stock_financial_us_analysis_indicator_em": {
                "fn": ak.stock_financial_us_analysis_indicator_em,
                "requires_symbol": True,
                "requires_indicator_us": True,
                "timeout": 600,
                "description": "美股-财务分析-主要指标-指定股票代码、指标类型"
            },
            "stock_financial_us_report_em": {
                "fn": ak.stock_financial_us_report_em,
                "requires_symbol": True,
                "requires_report_type": True,
                "requires_indicator_us": True,
                "timeout": 600,
                "param_mapping": {
                    "stock": "symbol",
                    "symbol": "report_type", 
                    "indicator": "indicator_us"
                },
                "description": "美股-财务分析-三大报表-指定股票代码、报表类型、指标类型"
            }
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
            
            # 处理股票代码和类别
            if config.get("requires_symbol"):
                symbol = tool_parameters.get("symbol", "")
                if not symbol:
                    yield self.create_text_message("此接口需要美股代码参数")
                    yield self.create_json_message({"error": "symbol required for this interface"})
                    return
                
                # 美股代码格式转换
                if symbol.startswith("US."):
                    # 去掉US前缀，如US.AAPL -> AAPL
                    symbol = symbol[3:]
                
                # 根据接口类型决定是否需要105.前缀
                # 只有历史数据接口需要105.前缀，财务分析接口使用原始格式
                if interface in ["stock_us_hist", "stock_us_hist_min_em"]:
                    # 历史数据接口需要105.前缀
                    if symbol.startswith("105."):
                        symbol = symbol.upper()
                    else:
                        if symbol.isalpha() and len(symbol) <= 6:
                            symbol = f"105.{symbol.upper()}"
                        else:
                            symbol = symbol.upper()
                else:
                    # 财务分析接口使用原始格式
                    symbol = symbol.upper()
                
                call_params["symbol"] = symbol
            
            # 处理知名美股类别
            if interface == "stock_us_famous_spot_em":
                category = tool_parameters.get("category", "科技类")
                call_params["symbol"] = category
            
            # 处理周期参数
            if config.get("requires_period"):
                period_type = config.get("period_type", "")
                if period_type == "historical":
                    # 历史行情接口使用周期一
                    period = tool_parameters.get("period", "daily")
                    call_params["period"] = period
                elif period_type == "minute":
                    # 分时行情接口使用周期二
                    period2 = tool_parameters.get("period2", "5")
                    call_params["period"] = period2
            
            # 处理日期范围
            if config.get("requires_date_range"):
                start_date = tool_parameters.get("start_date", "20250101")
                end_date = tool_parameters.get("end_date", "20250915")
                call_params["start_date"] = start_date
                call_params["end_date"] = end_date
            
            # 处理复权方式
            if config.get("requires_adjust"):
                adjust = tool_parameters.get("adjust", "none")
                if adjust == "none":
                    call_params["adjust"] = ""  # "none" 对应空字符串，表示不复权
                elif adjust:
                    call_params["adjust"] = adjust
            
            # 处理指标参数
            if config.get("requires_indicator_us"):
                indicator = tool_parameters.get("indicator_us", "年报")
                call_params["indicator"] = indicator
            
            # 处理报表类型
            if config.get("requires_report_type"):
                report_type = tool_parameters.get("report_type", "资产负债表")
                call_params["report_type"] = report_type
            
            # 处理参数映射（如果存在）
            param_mapping = config.get("param_mapping", {})
            if param_mapping:
                # 清空之前的参数，使用映射系统
                call_params = {}
                for ak_param, tool_param in param_mapping.items():
                    if tool_param == "symbol" and symbol:
                        call_params[ak_param] = symbol
                    elif tool_param == "report_type" and report_type:
                        call_params[ak_param] = report_type
                    elif tool_param == "indicator_us" and indicator:
                        call_params[ak_param] = indicator
            
            # 获取重试次数和超时时间
            retries = tool_parameters.get("retries", 5)
            timeout = tool_parameters.get("timeout", 600)
            
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
