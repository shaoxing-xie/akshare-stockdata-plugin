from collections.abc import Generator
from typing import Any
import pandas as pd
import logging

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .common_utils import process_dataframe_output, handle_akshare_error
from .stock_comprehensive_technical_indicators import (
    calculate_dynamic_valuation_indicators,
    ensure_json_serializable
)


class GetStockDynamicValuationTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            logging.info(f"GetStockDynamicValuationTool received parameters: {tool_parameters}")
            
            symbol = tool_parameters.get("symbol", "")
            retries = int(tool_parameters.get("retries", 5))
            timeout = float(tool_parameters.get("timeout", 600))
            
            logging.info(f"Symbol: {symbol}, Retries: {retries}, Timeout: {timeout}")
            
            if not symbol:
                yield self.create_text_message("股票代码不能为空")
                yield self.create_json_message({"error": "symbol required"})
                return
            
            # 计算动态估值指标
            valuation_result = calculate_dynamic_valuation_indicators(
                symbol, 
                retries, 
                timeout
            )
            
            if "error" in valuation_result:
                yield self.create_text_message(f"动态估值指标计算失败: {valuation_result['error']}")
                yield self.create_json_message({"error": valuation_result['error']})
                return
            
            # 将估值指标转换为DataFrame格式
            valuation_df = pd.DataFrame([valuation_result])
            
            # 确保所有列都是JSON序列化兼容的
            valuation_df = ensure_json_serializable(valuation_df)
            
            # 输出结果
            yield from process_dataframe_output(valuation_df, self)
                
        except Exception as e:
            yield from handle_akshare_error(e, self, f"计算动态估值指标")

