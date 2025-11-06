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


class GetHsgtRankingDataTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetHsgtRankingDataTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            symbol = tool_parameters.get("symbol", "")  # 排行类别
            market = tool_parameters.get("market", "")  # 沪深港通类别
            indicator = tool_parameters.get("indicator", "")  # 统计周期
            
            logging.info(f"Interface: {interface}, Symbol: {symbol}, Market: {market}, Indicator: {indicator}")
            
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
            "stock_hsgt_board_rank_em": {
                "fn": ak.stock_hsgt_board_rank_em,
                "requires_symbol": True,
                "symbol_type": "board_ranking",  # 板块排行类
                "requires_market": False,
                "requires_indicator": True,
                "indicator_type": "board_ranking",  # 板块排行类
                "requires_date_range": False,
                "description": "东方财富网-沪深港通持股-板块排行-指定排行类别和统计周期"
            },
            "stock_hsgt_hold_stock_em": {
                "fn": ak.stock_hsgt_hold_stock_em,
                "requires_symbol": False,
                "requires_market": True,
                "market_type": "stock_ranking",  # 个股排行类
                "requires_indicator": True,
                "indicator_type": "stock_ranking",  # 个股排行类
                "requires_date_range": False,
                "description": "东方财富网-沪深港通持股-个股排行-指定沪深港通类别和统计周期"
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
            if symbol_type == "board_ranking" and not symbol:
                yield self.create_text_message("请提供排行类别参数")
                yield self.create_json_message({"error": "symbol required for board_ranking type", "received_params": tool_parameters})
                return
        
        if config.get("requires_market", False):
            market_type = config.get("market_type", "")
            if market_type == "stock_ranking" and not market:
                yield self.create_text_message("请提供沪深港通类别参数")
                yield self.create_json_message({"error": "market required for stock_ranking type", "received_params": tool_parameters})
                return
        
        if config.get("requires_indicator", False):
            if not indicator:
                yield self.create_text_message("请提供统计周期参数")
                yield self.create_json_message({"error": "indicator required", "received_params": tool_parameters})
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
                if symbol_type == "board_ranking":
                    if not symbol:
                        yield from handle_akshare_error(
                            ValueError("缺少必需参数：排行类别"), 
                            self, 
                            f"接口: {interface}"
                        )
                        return
                    call_params["symbol"] = symbol
            
            if config.get("requires_market", False):
                market_type = config.get("market_type", "")
                if market_type == "stock_ranking":
                    if not market:
                        yield from handle_akshare_error(
                            ValueError("缺少必需参数：沪深港通类别"), 
                            self, 
                            f"接口: {interface}"
                        )
                        return
                    call_params["market"] = market
            
            if config.get("requires_indicator", False):
                # 根据接口类型确定指标参数格式 - 从原工具迁移
                indicator_type = config.get("indicator_type", "")
                if indicator_type == "board_ranking":
                    # 板块排行接口直接使用indicator
                    call_params["indicator"] = indicator
                elif indicator_type == "stock_ranking":
                    # 个股排行接口需要转换格式 - 从原工具迁移
                    indicator_mapping = {
                        "今日": "今日排行",
                        "3日": "3日排行", 
                        "5日": "5日排行",
                        "10日": "10日排行",
                        "1月": "月排行",
                        "1季": "季排行",
                        "1年": "年排行"
                    }
                    
                    # 转换指标格式
                    mapped_indicator = indicator_mapping.get(indicator, indicator)
                    call_params["indicator"] = mapped_indicator
                else:
                    # 其他接口直接使用indicator
                    call_params["indicator"] = indicator
            
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
                yield from handle_akshare_error(e, self, f"接口: {interface}, 类别: {symbol}, 市场: {market}, 统计周期: {indicator}", str(timeout))
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
            logging.error(f"GetHsgtRankingDataTool error: {e}")
            text, payload = build_error_payload(e)
            yield self.create_text_message(text)
            yield self.create_json_message(payload)
            return

