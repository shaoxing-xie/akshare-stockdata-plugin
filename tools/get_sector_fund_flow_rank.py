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


class GetSectorFundFlowRankTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetSectorFundFlowRankTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            indicator = tool_parameters.get("indicator", "")  # 统计周期
            sector_type = tool_parameters.get("sector_type", "")  # 板块类型
            symbol = tool_parameters.get("symbol", "")  # 排行类别
            
            logging.info(f"Interface: {interface}, Indicator: {indicator}, SectorType: {sector_type}, Symbol: {symbol}")
            
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
            "stock_sector_fund_flow_rank": {
                "fn": ak.stock_sector_fund_flow_rank,
                "requires_indicator": True,
                "requires_sector_type": True,
                "description": "东方财富网-板块资金流-排名-指定统计周期、板块类型"
            },
            "stock_fund_flow_concept": {
                "fn": ak.stock_fund_flow_concept,
                "requires_symbol": True,
                "description": "同花顺-概念资金流-指定排行类别"
            },
            "stock_fund_flow_industry": {
                "fn": ak.stock_fund_flow_industry,
                "requires_symbol": True,
                "description": "同花顺-行业资金流-指定排行类别"
            },
        }
        
        # 获取接口配置
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"未知的接口: {interface}")
            yield self.create_json_message({"error": f"unknown interface: {interface}"})
            return
        
        # 根据接口配置验证必需参数 - 从原工具迁移
        if config.get("requires_indicator", False) and not indicator:
            yield self.create_text_message("请提供统计周期参数（今日/5日/10日）")
            yield self.create_json_message({"error": "indicator required", "received_params": tool_parameters})
            return
        
        # 特殊验证：某些接口不支持"3日"指标
        if indicator == "3日":
            if interface == "stock_sector_fund_flow_rank":
                yield self.create_text_message("错误：'东方财富网-板块资金流-排名'接口不支持 '3日' 指标。\n\n该接口支持的指标选项为：今日、5日、10日。\n请选择正确的指标参数。")
                yield self.create_json_message({"error": "invalid_indicator", "message": f"{interface} does not support '3日' indicator, only supports: 今日, 5日, 10日"})
                return
        
        if config.get("requires_sector_type", False) and not sector_type:
            yield self.create_text_message("请提供板块类型参数（行业资金流/概念资金流/地域资金流）")
            yield self.create_json_message({"error": "sector_type required", "received_params": tool_parameters})
            return
        
        if config.get("requires_symbol", False) and not symbol:
            yield self.create_text_message("请提供排行类别参数（即时/3日排行/5日排行/10日排行/20日排行）")
            yield self.create_json_message({"error": "symbol required", "received_params": tool_parameters})
            return
        
        try:
            # 网络参数 - 统一处理逻辑 - 从原工具迁移
            retries = int(tool_parameters.get("retries", 5))
            timeout_param = tool_parameters.get("timeout")
            timeout = float(timeout_param) if timeout_param is not None else None
            logging.info(f"Network params - retries: {retries}, timeout: {timeout}")
            
            # 构建调用参数 - 根据接口要求动态构建 - 从原工具迁移
            call_params = {}
            
            if config.get("requires_indicator", False) and indicator:
                call_params["indicator"] = indicator
            if config.get("requires_sector_type", False) and sector_type:
                call_params["sector_type"] = sector_type
            if config.get("requires_symbol", False) and symbol:
                call_params["symbol"] = symbol
            
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
                # 其他错误 - 从原工具迁移
                param_info = f"接口: {interface}"
                if indicator:
                    param_info += f", 统计周期: {indicator}"
                if sector_type:
                    param_info += f", 板块类型: {sector_type}"
                if symbol:
                    param_info += f", 排行类别: {symbol}"
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
            logging.error(f"GetSectorFundFlowRankTool error: {e}")
            text, payload = build_error_payload(e)
            yield self.create_text_message(text)
            yield self.create_json_message(payload)
            return

