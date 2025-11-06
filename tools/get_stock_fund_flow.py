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
    handle_akshare_error,
    validate_stock_symbol
)


class GetStockFundFlowTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetStockFundFlowTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            stock_code = tool_parameters.get("stock_code", "")  # 股票代码
            market = tool_parameters.get("market", "")  # 市场
            
            logging.info(f"Interface: {interface}, StockCode: {stock_code}, Market: {market}")
            
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
            "stock_individual_fund_flow": {
                "fn": ak.stock_individual_fund_flow,
                "requires_stock_code": True,
                "requires_market": True,
                "description": "东方财富网-个股资金流向-指定股票、证交所"
            },
        }
        
        # 获取接口配置
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"未知的接口: {interface}")
            yield self.create_json_message({"error": f"unknown interface: {interface}"})
            return
        
        # 根据接口配置验证必需参数 - 从原工具迁移
        if config.get("requires_stock_code", False) and not stock_code:
            yield self.create_text_message("请提供股票代码（如：600519、000001 等）")
            yield self.create_json_message({"error": "stock_code required", "received_params": tool_parameters})
            return
        
        if config.get("requires_market", False) and not market:
            yield self.create_text_message("请提供证交所代码（sh/sz/bj）")
            yield self.create_json_message({"error": "market required", "received_params": tool_parameters})
            return
        
        # 股票代码格式验证（仅对需要股票代码的接口）- 从原工具迁移
        if config.get("requires_stock_code", False) and stock_code:
            validation_result = None
            for result in validate_stock_symbol(stock_code, self):
                if isinstance(result, bool):
                    validation_result = result
                else:
                    yield result
            if validation_result is False:
                return
            
            # 验证市场参数与股票代码的匹配性
            if config.get("requires_market", False) and market and stock_code:
                if not self._validate_market_symbol_match(stock_code, market):
                    yield self.create_text_message(f"错误：股票代码 '{stock_code}' 与市场 '{market}' 不匹配。\n\n请检查：\n- 600xxx、601xxx、603xxx、688xxx、689xxx 对应 'sh'（上海）\n- 000xxx、001xxx、002xxx、003xxx、300xxx 对应 'sz'（深圳）\n- 430xxx、830xxx、870xxx 对应 'bj'（北京）")
                    yield self.create_json_message({"error": "market_symbol_mismatch", "message": f"Stock symbol '{stock_code}' does not match market '{market}'"})
                    return
        
        try:
            # 网络参数 - 统一处理逻辑 - 从原工具迁移
            retries = int(tool_parameters.get("retries", 5))
            timeout_param = tool_parameters.get("timeout")
            timeout = float(timeout_param) if timeout_param is not None else None
            logging.info(f"Network params - retries: {retries}, timeout: {timeout}")
            
            # 构建调用参数 - 根据接口要求动态构建 - 从原工具迁移
            call_params = {}
            
            if config.get("requires_stock_code", False) and stock_code:
                call_params["stock"] = stock_code
            if config.get("requires_market", False) and market:
                call_params["market"] = market
            
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
                yield from handle_akshare_error(e, self, f"接口: {interface}, 股票代码: {stock_code}, 市场: {market}", str(timeout))
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
            logging.error(f"GetStockFundFlowTool error: {e}")
            text, payload = build_error_payload(e)
            yield self.create_text_message(text)
            yield self.create_json_message(payload)
            return
    
    def _validate_market_symbol_match(self, symbol: str, market: str) -> bool:
        """
        验证市场参数与股票代码的匹配性
        
        Args:
            symbol: 股票代码
            market: 市场代码
            
        Returns:
            bool: 是否匹配
        """
        if not symbol or not market:
            return True  # 如果任一为空，跳过验证
            
        symbol = symbol.strip().upper()
        market = market.strip().lower()
        
        # 移除市场前缀（如SH、SZ等）
        clean_symbol = symbol.replace('SH', '').replace('SZ', '').replace('HK', '').replace('-', '').replace('.', '')
        
        # 上海证券交易所：600xxx, 601xxx, 603xxx, 688xxx, 689xxx
        if clean_symbol.startswith(('600', '601', '603', '688', '689')):
            return market == 'sh'
        # 深圳证券交易所：000xxx, 001xxx, 002xxx, 003xxx, 300xxx
        elif clean_symbol.startswith(('000', '001', '002', '003', '300')):
            return market == 'sz'
        # 北京证券交易所：430xxx, 830xxx, 870xxx
        elif clean_symbol.startswith(('430', '830', '870')):
            return market == 'bj'
        else:
            return True  # 无法识别的代码，跳过验证

