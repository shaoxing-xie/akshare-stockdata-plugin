from collections.abc import Generator
from typing import Any
import pandas as pd
import logging

import akshare as ak
from provider.akshare_stockdata import safe_ak_call
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .common_utils import process_dataframe_output, handle_akshare_error
from .stock_comprehensive_technical_indicators import (
    preprocess_data_for_indicators,
    calculate_historical_valuation_indicators,
    optimize_dataframe_memory,
    ensure_json_serializable,
    get_indicator_columns
)


class GetStockHistoricalValuationTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            logging.info(f"GetStockHistoricalValuationTool received parameters: {tool_parameters}")
            
            symbol = tool_parameters.get("symbol", "")
            period = tool_parameters.get("period", "daily")
            start_date = tool_parameters.get("start_date", "20250101")
            end_date = tool_parameters.get("end_date", "")
            adjust = tool_parameters.get("adjust", "qfq")
            retries = int(tool_parameters.get("retries", 5))
            timeout = float(tool_parameters.get("timeout", 600))
            
            # 处理复权方式参数
            if adjust == "none":
                adjust = ""
            
            # 处理结束日期缺省值（当前日期）
            if not end_date:
                from datetime import datetime
                end_date = datetime.now().strftime("%Y%m%d")
            
            logging.info(f"Symbol: {symbol}, Period: {period}, StartDate: {start_date}, EndDate: {end_date}, Adjust: {adjust}")
            
            if not symbol:
                yield self.create_text_message("股票代码不能为空")
                yield self.create_json_message({"error": "symbol required"})
                return
            
            # 获取历史行情数据
            result = safe_ak_call(
                ak.stock_zh_a_hist,
                retries=retries,
                timeout=timeout,
                symbol=symbol,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )
            
            if result is None or result.empty or len(result.columns) == 0:
                yield self.create_text_message("暂无历史数据，可能是无效的股票代码")
                yield self.create_json_message({"error": "no data returned"})
                return
            
            # 预处理数据
            df = preprocess_data_for_indicators(result)
            
            # 计算历史估值指标
            df = calculate_historical_valuation_indicators(df, symbol, retries, timeout)
            
            # 选择输出列
            output_columns = get_indicator_columns("historical_valuation_indicators", period)
            available_columns = [col for col in output_columns if col in df.columns]
            result_df = df[available_columns].copy()
            
            # 优化内存使用
            result_df = optimize_dataframe_memory(result_df)
            
            # 确保日期列是字符串格式
            if '日期' in result_df.columns:
                result_df['日期'] = result_df['日期'].dt.strftime('%Y-%m-%d')
            
            # 确保所有列都是JSON序列化兼容的
            result_df = ensure_json_serializable(result_df)
            
            # 输出结果
            yield from process_dataframe_output(result_df, self)
                
        except Exception as e:
            yield from handle_akshare_error(e, self, f"计算历史估值指标")

