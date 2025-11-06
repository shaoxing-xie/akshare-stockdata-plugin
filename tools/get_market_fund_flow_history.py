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


class GetMarketFundFlowHistoryTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetMarketFundFlowHistoryTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            industry_name = tool_parameters.get("industry_name", "")  # 行业名称
            concept_name = tool_parameters.get("concept_name", "")  # 概念名称
            
            logging.info(f"Interface: {interface}, IndustryName: {industry_name}, ConceptName: {concept_name}")
            
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
            "stock_market_fund_flow": {
                "fn": ak.stock_market_fund_flow,
                "requires_industry_name": False,
                "requires_concept_name": False,
                "description": "东方财富网-资金流向-大盘-历史数据"
            },
            "stock_sector_fund_flow_hist": {
                "fn": ak.stock_sector_fund_flow_hist,
                "requires_industry_name": True,
                "requires_concept_name": False,
                "description": "东方财富网-行业历史资金流-指定行业名称"
            },
            "stock_concept_fund_flow_hist": {
                "fn": ak.stock_concept_fund_flow_hist,
                "requires_industry_name": False,
                "requires_concept_name": True,
                "description": "东方财富网-概念历史资金流-指定概念名称"
            },
        }
        
        # 获取接口配置
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"未知的接口: {interface}")
            yield self.create_json_message({"error": f"unknown interface: {interface}"})
            return
        
        # 根据接口配置验证必需参数 - 从原工具迁移
        if config.get("requires_industry_name", False) and not industry_name:
            yield self.create_text_message("请提供行业名称参数（如：汽车服务、电源设备等）")
            yield self.create_json_message({"error": "industry_name required", "received_params": tool_parameters})
            return
        
        if config.get("requires_concept_name", False) and not concept_name:
            yield self.create_text_message("请提供概念名称参数（如：数据要素、租售同权等）")
            yield self.create_json_message({"error": "concept_name required", "received_params": tool_parameters})
            return
        
        try:
            # 网络参数 - 统一处理逻辑 - 从原工具迁移
            retries = int(tool_parameters.get("retries", 5))
            timeout_param = tool_parameters.get("timeout")
            timeout = float(timeout_param) if timeout_param is not None else None
            logging.info(f"Network params - retries: {retries}, timeout: {timeout}")
            
            # 构建调用参数 - 根据接口要求动态构建 - 从原工具迁移
            call_params = {}
            
            if config.get("requires_industry_name", False) and industry_name:
                call_params["symbol"] = industry_name
            if config.get("requires_concept_name", False) and concept_name:
                call_params["symbol"] = concept_name
            
            logging.info(f"Call params: {call_params}")
            logging.info(f"Function: {config['fn']}")
            
            # 调用AKShare接口 - 从原工具迁移
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
                if "'noneType' object is not subscriptable" in lower_msg or "KeyError" in error_msg:
                    # 友好提醒：强调检查参数取值是否正确（如行业名称或概念名称无对应数据）- 从原工具迁移
                    if config.get("requires_industry_name", False):
                        friendly_msg = (
                            "数据源返回为空，无法解析\n\n"
                            "可能原因：\n"
                            "1) 行业名称不存在或格式不正确\n"
                            "2) 数据源暂时不可用或结构变更\n\n"
                            "请检查参数是否正确：\n"
                            f"- 行业名称(industry_name) 示例：汽车服务、电源设备\n"
                            "- 可尝试更换行业名称或稍后重试"
                        )
                    else:
                        friendly_msg = (
                            "数据源返回为空，无法解析\n\n"
                            "可能原因：\n"
                            "1) 概念名称不存在或格式不正确\n"
                            "2) 数据源暂时不可用或结构变更\n\n"
                            "请检查参数是否正确：\n"
                            f"- 概念名称(concept_name) 示例：数据要素、租售同权\n"
                            "- 可尝试更换概念名称或稍后重试"
                        )
                    yield self.create_text_message(friendly_msg)
                    yield self.create_json_message({
                        "error": "empty_result_or_invalid_parameter",
                        "message": "返回数据为空或参数无效",
                        "details": error_msg,
                        "suggestion": "请核对名称是否正确，或稍后重试"
                    })
                    return
                # 其他错误 - 从原工具迁移
                param_info = f"接口: {interface}"
                if industry_name:
                    param_info += f", 行业名称: {industry_name}"
                if concept_name:
                    param_info += f", 概念名称: {concept_name}"
                yield from handle_akshare_error(e, self, param_info, str(timeout))
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
            logging.error(f"GetMarketFundFlowHistoryTool error: {e}")
            text, payload = build_error_payload(e)
            yield self.create_text_message(text)
            yield self.create_json_message(payload)
            return

