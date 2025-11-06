from collections.abc import Generator
from typing import Any
import pandas as pd

import akshare as ak
from provider.akshare_stockdata import safe_ak_call
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .common_utils import process_dataframe_output, process_other_output, handle_akshare_error


class GetTechnicalContinuousRiseFallTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetTechnicalContinuousRiseFallTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            retries = int(tool_parameters.get("retries", 5))
            timeout = float(tool_parameters.get("timeout", 120))
            
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
        
        # 定义接口配置
        interface_configs = {
            "stock_rank_lxsz_ths": {
                "fn": ak.stock_rank_lxsz_ths,
                "timeout": 120,
                "description": "同花顺-技术选股-连续上涨"
            },
            "stock_rank_lxxd_ths": {
                "fn": ak.stock_rank_lxxd_ths,
                "timeout": 120,
                "description": "同花顺-技术选股-连续下跌"
            },
        }
        
        # 获取接口配置
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"未知的接口: {interface}")
            yield self.create_json_message({"error": f"unknown interface: {interface}"})
            return
        
        # 构建调用参数
        try:
            call_params = {}
            
            # 使用接口特定的超时时间
            interface_timeout = config.get("timeout", timeout)
            
            logging.info(f"Final call params: {call_params}")
            logging.info(f"Using timeout: {interface_timeout}")
            
        except Exception as e:
            logging.error(f"Error in parameter building: {e}")
            yield self.create_text_message(f"参数构建错误: {e}")
            yield self.create_json_message({"error": f"parameter building error: {e}"})
            return
        
        # 调用AKShare接口
        try:
            result = safe_ak_call(
                config["fn"],
                retries=retries,
                timeout=interface_timeout,
                **call_params
            )
            
            if result is None:
                yield self.create_text_message("接口返回空数据")
                yield self.create_json_message({"data": []})
                return
            
            # 处理返回结果
            if isinstance(result, pd.DataFrame):
                if result.empty:
                    yield self.create_text_message("暂无数据")
                    yield self.create_json_message({"data": []})
                else:
                    # 处理DataFrame输出
                    yield from process_dataframe_output(result, self)
            else:
                # 处理其他类型输出
                yield from process_other_output(result, self)
                
        except Exception as e:
            logging.error(f"Error in AKShare call: {e}")
            
            # 检查是否是网络连接错误
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ["ssl", "timeout", "read timed out", "connection", "max retries exceeded", "chunkedencoding", "response ended prematurely"]):
                yield self.create_text_message(f"网络连接中断，请稍后重试\n\n错误详情: {e}")
                yield self.create_json_message({
                    "error": "network_error",
                    "message": "网络连接中断",
                    "details": str(e),
                    "suggestion": "请稍后重试或检查网络连接"
                })
            else:
                # 其他错误
                yield from handle_akshare_error(e, self, f"接口: {interface}", str(interface_timeout))

