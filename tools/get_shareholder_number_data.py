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


class GetShareholderNumberDataTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetShareholderNumberDataTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            gdhs_date = tool_parameters.get("gdhs_date", "最新")
            logging.info(f"Interface: {interface}, GDHS Date: {gdhs_date}")
            
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
            "stock_zh_a_gdhs": {
                "fn": ak.stock_zh_a_gdhs,
                "requires_gdhs_date": True,
                "description": "东方财富网-股东户数数据-指定日期"
            },
        }
        
        # 获取接口配置
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"未知的接口: {interface}")
            yield self.create_json_message({"error": f"unknown interface: {interface}"})
            return
        
        try:
            # 网络参数
            retries = int(tool_parameters.get("retries", 5))
            timeout = float(tool_parameters.get("timeout", 240))
            
            # 构建调用参数
            call_params = {}
            
            # 处理股东户数日期参数
            if config.get("requires_gdhs_date"):
                if not gdhs_date:
                    yield self.create_text_message("此接口需要股东户数日期参数")
                    yield self.create_json_message({"error": "gdhs_date required for this interface"})
                    return
                # stock_zh_a_gdhs 使用 symbol 参数，但参数值为日期
                call_params["symbol"] = gdhs_date
            
            logging.info(f"Call params: {call_params}")
            logging.info(f"Function: {config['fn']}")
            logging.info(f"Interface: {interface}, GDHS Date: {gdhs_date}")
            
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
    

