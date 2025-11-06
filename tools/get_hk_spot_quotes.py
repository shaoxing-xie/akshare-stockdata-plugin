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


class GetHkSpotQuotesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetHkSpotQuotesTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            retries = int(tool_parameters.get("retries", 5))
            timeout = float(tool_parameters.get("timeout", 600))
            
            logging.info(f"Interface: {interface}, Retries: {retries}, Timeout: {timeout}")
            
            if not interface:
                yield self.create_text_message("请选择要调用的接口")
                yield self.create_json_message({"error": "interface required", "received_params": tool_parameters})
                return
                
        except Exception as e:
            logging.error(f"Error in _invoke start: {e}")
            yield self.create_text_message(f"参数处理错误: {e}")
            yield self.create_json_message({"error": f"parameter processing error: {e}"})
            return
        
        # 定义接口配置 - 完全按照原工具stock_hk_data的实现
        interface_configs = {
            "stock_hk_spot_em": {
                "fn": ak.stock_hk_spot_em,
                "description": "港股-实时行情(延15分钟)"
            },
            "stock_hk_spot": {
                "fn": ak.stock_hk_spot,
                "description": "新浪-港股-实时行情(延15分钟)"
            },
            "stock_hk_main_board_spot_em": {
                "fn": ak.stock_hk_main_board_spot_em,
                "description": "港股主板-实时行情(延15分钟)"
            },
            "stock_hk_famous_spot_em": {
                "fn": ak.stock_hk_famous_spot_em,
                "description": "知名港股实时行情数据"
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

