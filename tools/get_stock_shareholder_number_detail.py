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
    handle_akshare_error,
    validate_stock_symbol
)


class GetStockShareholderNumberDetailTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetStockShareholderNumberDetailTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            symbol = tool_parameters.get("symbol", "")
            retries = int(tool_parameters.get("retries", 5))
            timeout = float(tool_parameters.get("timeout", 240))
            
            logging.info(f"Interface: {interface}, Symbol: {symbol}, Retries: {retries}, Timeout: {timeout}")
            
            if not interface:
                yield self.create_text_message("请选择要调用的接口")
                yield self.create_json_message({"error": "interface required", "received_params": tool_parameters})
                return
            
            # 验证股票代码
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
            "stock_zh_a_gdhs_detail_em": {
                "fn": ak.stock_zh_a_gdhs_detail_em,
                "requires_symbol": True,
                "description": "东方财富网-股东户数详情-指定股票"
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
                # 处理股票代码格式（移除市场前缀，如果需要）
                processed_symbol = symbol
                if symbol.upper().startswith(('SH', 'SZ', 'HK')):
                    processed_symbol = symbol[2:]
                call_params["symbol"] = processed_symbol
            
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

