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


class GetHsgtFundFlowDataTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetHsgtFundFlowDataTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            fund_category = tool_parameters.get("fund_category", "")  # 资金类别
            historical_data_category = tool_parameters.get("historical_data_category", "")  # 历史数据类别
            
            logging.info(f"Interface: {interface}, Fund Category: {fund_category}, Historical Data Category: {historical_data_category}")
            
            # 验证必需参数
            if not interface:
                yield self.create_text_message("请选择要调用的接口")
                yield self.create_json_message({"error": "interface required", "received_params": tool_parameters})
                return
                
        except Exception as e:
            logging.error(f"Error in _invoke start: {e}")
            yield self.create_text_message(f"参数处理错误: {e}")
            yield self.create_json_message({"error": f"parameter processing error: {e}"})
            return
        
        # 定义接口配置 - 从原工具迁移
        interface_configs = {
            "stock_hsgt_fund_min_em": {
                "fn": ak.stock_hsgt_fund_min_em,
                "requires_symbol": True,
                "symbol_type": "fund_flow",  # 资金流向类
                "requires_market": False,
                "requires_indicator": False,
                "requires_date_range": False,
                "description": "东方财富网-沪深港通-市场概括-分时数据-指定资金类别"
            },
            "stock_hsgt_fund_flow_summary_em": {
                "fn": ak.stock_hsgt_fund_flow_summary_em,
                "requires_symbol": False,
                "requires_market": False,
                "requires_indicator": False,
                "requires_date_range": False,
                "description": "东方财富网-沪深港通资金流向"
            },
            "stock_hsgt_hist_em": {
                "fn": ak.stock_hsgt_hist_em,
                "requires_symbol": True,
                "symbol_type": "historical_data",  # 历史数据类
                "requires_market": False,
                "requires_indicator": False,
                "requires_date_range": False,
                "description": "东方财富网-沪深港通资金流向-历史数据-指定历史数据类别"
            },
        }
        
        # 获取接口配置
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"未知的接口: {interface}")
            yield self.create_json_message({"error": f"unknown interface: {interface}"})
            return
        
        # 根据接口配置验证必需参数 - 从原工具迁移
        if config.get("requires_symbol", False):
            symbol_type = config.get("symbol_type", "")
            if symbol_type == "fund_flow" and not fund_category:
                yield self.create_text_message("请提供资金类别参数（北向资金或南向资金）")
                yield self.create_json_message({"error": "fund_category required for fund_flow type", "received_params": tool_parameters})
                return
            elif symbol_type == "historical_data" and not historical_data_category:
                yield self.create_text_message("请提供历史数据类别参数（北向资金、沪股通、深股通、南向资金、港股通沪或港股通深）")
                yield self.create_json_message({"error": "historical_data_category required for historical_data type", "received_params": tool_parameters})
                return
        
        try:
            # 网络参数 - 统一处理逻辑 - 从原工具迁移
            retries = int(tool_parameters.get("retries", 5))
            timeout_param = tool_parameters.get("timeout")  # 让子进程根据接口类型自动决定超时时间
            timeout = float(timeout_param) if timeout_param is not None else None
            logging.info(f"Network params - retries: {retries}, timeout: {timeout} (auto-determined by interface type)")
            
            # 构建调用参数 - 根据接口要求动态构建 - 从原工具迁移
            call_params = {}
            
            # 根据接口要求添加参数 - 从原工具迁移
            if config.get("requires_symbol", False):
                symbol_type = config.get("symbol_type", "")
                if symbol_type == "fund_flow":
                    if not fund_category:
                        yield from handle_akshare_error(
                            ValueError("缺少必需参数：资金类别"), 
                            self, 
                            f"接口: {interface}"
                        )
                        return
                    call_params["symbol"] = fund_category
                elif symbol_type == "historical_data":
                    if not historical_data_category:
                        yield from handle_akshare_error(
                            ValueError("缺少必需参数：历史数据类别"), 
                            self, 
                            f"接口: {interface}"
                        )
                        return
                    call_params["symbol"] = historical_data_category
            
            logging.info(f"Call params: {call_params}")
            logging.info(f"Function: {config['fn']}")
            
            # 调用AKShare接口 - timeout现在仅用于子进程超时控制 - 从原工具迁移
            try:
                result = safe_ak_call(
                    config["fn"],
                    retries=retries,
                    timeout=timeout,
                    **call_params
                )
            except Exception as e:
                # 检查是否是已知的AKShare接口问题或网络问题 - 从原工具迁移
                error_msg = str(e)
                lower_msg = error_msg.lower()
                # 网络相关错误统一提示（与其它工具保持一致关键词）
                if any(k in lower_msg for k in ["ssl", "timeout", "read timed out", "connection", "max retries exceeded", "chunkedencoding", "response ended prematurely"]):
                    yield self.create_text_message(f"网络连接中断，请稍后重试\n\n错误详情: {error_msg}")
                    yield self.create_json_message({
                        "error": "network_error",
                        "message": "网络连接中断",
                        "details": error_msg,
                        "suggestion": "请稍后重试或检查网络连接"
                    })
                    return
                # 其他错误 - 从原工具迁移
                category_info = fund_category if config.get("symbol_type") == "fund_flow" else historical_data_category
                yield from handle_akshare_error(e, self, f"接口: {interface}, 类别: {category_info}", str(timeout))
                return
            
            # 处理结果 - 从原工具迁移
            if result is None:
                yield from handle_empty_result(self)
                return
            
            # 检查是否为空
            if hasattr(result, 'empty') and result.empty:
                yield from handle_empty_result(self)
                return
            
            # 输出处理 - 从原工具迁移
            if isinstance(result, pd.DataFrame):
                yield from process_dataframe_output(result, self)
            else:
                yield from process_other_output(result, self)
                
        except Exception as e:
            import logging
            logging.error(f"GetHsgtFundFlowDataTool error: {e}")
            text, payload = build_error_payload(e)
            yield self.create_text_message(text)
            yield self.create_json_message(payload)
            return

