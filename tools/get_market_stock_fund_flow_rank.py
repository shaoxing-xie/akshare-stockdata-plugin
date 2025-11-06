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


class GetMarketStockFundFlowRankTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetMarketStockFundFlowRankTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            indicator = tool_parameters.get("indicator", "")  # 统计周期
            market_choice = tool_parameters.get("market_choice", "")  # 市场选择
            symbol = tool_parameters.get("symbol", "")  # 排行类别
            industry_name = tool_parameters.get("industry_name", "")  # 行业名称
            
            logging.info(f"Interface: {interface}, Indicator: {indicator}, MarketChoice: {market_choice}, Symbol: {symbol}, IndustryName: {industry_name}")
            
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
            "stock_individual_fund_flow_rank": {
                "fn": ak.stock_individual_fund_flow_rank,
                "requires_indicator": True,
                "description": "东方财富网-资金流向-排名-指定统计周期"
            },
            "stock_main_fund_flow": {
                "fn": ak.stock_main_fund_flow,
                "requires_market_choice": True,
                "description": "东方财富网-主力净流入排名-指定市场选择"
            },
            "stock_fund_flow_individual": {
                "fn": ak.stock_fund_flow_individual,
                "requires_symbol": True,
                "description": "同花顺-个股资金流-指定排行类别"
            },
            "stock_sector_fund_flow_summary": {
                "fn": ak.stock_sector_fund_flow_summary,
                "requires_industry_name": True,
                "requires_indicator": True,
                "description": "东方财富网-行业资金流-xx行业个股资金流-指定行业名称、统计周期"
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
            yield self.create_text_message("请提供统计周期参数（今日/3日/5日/10日）")
            yield self.create_json_message({"error": "indicator required", "received_params": tool_parameters})
            return
        
        # 特殊验证：某些接口不支持"3日"指标
        if indicator == "3日":
            if interface == "stock_sector_fund_flow_summary":
                yield self.create_text_message("错误：'东方财富网-行业资金流-xx行业个股资金流'接口不支持 '3日' 指标。\n\n该接口支持的指标选项为：今日、5日、10日。\n请选择正确的指标参数。")
                yield self.create_json_message({"error": "invalid_indicator", "message": f"{interface} does not support '3日' indicator, only supports: 今日, 5日, 10日"})
                return
        
        if config.get("requires_market_choice", False) and not market_choice:
            yield self.create_text_message("请提供市场选择参数（全部股票/沪深A股/科创板/创业板等）")
            yield self.create_json_message({"error": "market_choice required", "received_params": tool_parameters})
            return
        
        if config.get("requires_symbol", False) and not symbol:
            yield self.create_text_message("请提供排行类别参数（即时/3日排行/5日排行/10日排行/20日排行）")
            yield self.create_json_message({"error": "symbol required", "received_params": tool_parameters})
            return
        
        if config.get("requires_industry_name", False) and not industry_name:
            yield self.create_text_message("请提供行业名称参数（如：汽车服务、电源设备等）")
            yield self.create_json_message({"error": "industry_name required", "received_params": tool_parameters})
            return
        
        try:
            # 网络参数 - 统一处理逻辑 - 从原工具迁移
            retries = int(tool_parameters.get("retries", 5))
            timeout_param = tool_parameters.get("timeout")
            timeout = float(timeout_param) if timeout_param is not None else None
            logging.info(f"Network params - retries: {retries}, timeout: {timeout}")
            
            # 构建调用参数 - 根据接口要求动态构建 - 从原工具迁移
            call_params = {}
            
            if interface == "stock_individual_fund_flow_rank":
                # 东方财富网-资金流向-排名
                if indicator:
                    call_params["indicator"] = indicator
            elif interface == "stock_main_fund_flow":
                # 东方财富网-主力净流入排名
                if market_choice:
                    call_params["symbol"] = market_choice
            elif interface == "stock_fund_flow_individual":
                # 同花顺-个股资金流
                if symbol:
                    call_params["symbol"] = symbol
            elif interface == "stock_sector_fund_flow_summary":
                # 东方财富网-行业资金流-xx行业个股资金流
                if industry_name:
                    call_params["symbol"] = industry_name
                if indicator:
                    call_params["indicator"] = indicator
            
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
                if "'noneType' object is not subscriptable" in lower_msg:
                    # 友好提醒：强调检查参数取值是否正确（如行业名称无对应数据）- 从原工具迁移
                    friendly_msg = (
                        "数据源返回为空，无法解析\n\n"
                        "可能原因：\n"
                        "1) 行业名称不存在或格式不正确\n"
                        "2) 数据源暂时不可用或结构变更\n\n"
                        "请检查参数是否正确：\n"
                        "- 行业名称(industry_name) 示例：汽车服务、电源设备\n"
                        "- 可尝试更换行业名称或稍后重试"
                    )
                    yield self.create_text_message(friendly_msg)
                    yield self.create_json_message({
                        "error": "empty_result_or_invalid_parameter",
                        "message": "返回数据为空或参数无效",
                        "details": error_msg,
                        "suggestion": "请核对行业名称是否存在，或稍后重试"
                    })
                    return
                # 其他错误 - 从原工具迁移
                param_info = f"接口: {interface}"
                if indicator:
                    param_info += f", 统计周期: {indicator}"
                if market_choice:
                    param_info += f", 市场选择: {market_choice}"
                if symbol:
                    param_info += f", 排行类别: {symbol}"
                if industry_name:
                    param_info += f", 行业名称: {industry_name}"
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
            logging.error(f"GetMarketStockFundFlowRankTool error: {e}")
            text, payload = build_error_payload(e)
            yield self.create_text_message(text)
            yield self.create_json_message(payload)
            return

