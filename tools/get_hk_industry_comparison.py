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


class GetHkIndustryComparisonTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetHkIndustryComparisonTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            symbol = tool_parameters.get("stock_code", "")  # 港股代码
            retries = int(tool_parameters.get("retries", 5))
            timeout = float(tool_parameters.get("timeout", 600))
            
            logging.info(f"Interface: {interface}, Symbol: {symbol}, Retries: {retries}, Timeout: {timeout}")
            
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
            "stock_hk_growth_comparison_em": {
                "fn": ak.stock_hk_growth_comparison_em,
                "requires_symbol": True,
                "description": "东方财富网-港股-行业对比-成长性对比-指定股票代码"
            },
            "stock_hk_valuation_comparison_em": {
                "fn": ak.stock_hk_valuation_comparison_em,
                "requires_symbol": True,
                "description": "东方财富网-港股-行业对比-估值对比-指定股票代码"
            },
            "stock_hk_scale_comparison_em": {
                "fn": ak.stock_hk_scale_comparison_em,
                "requires_symbol": True,
                "description": "东方财富网-港股-行业对比-规模对比-指定股票代码"
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
            
            # 处理股票代码
            if config.get("requires_symbol"):
                if not symbol:
                    yield self.create_text_message("此接口需要港股代码参数")
                    yield self.create_json_message({"error": "symbol required for this interface"})
                    return
                
                # 港股代码格式转换
                if symbol.startswith("HK"):
                    # 去掉HK前缀，如HK00700 -> 00700
                    symbol = symbol[2:]
                
                # 行业对比接口保持5位格式
                call_params["symbol"] = symbol
            
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

