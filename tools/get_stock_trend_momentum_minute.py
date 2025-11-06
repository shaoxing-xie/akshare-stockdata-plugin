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
    calculate_trend_momentum_oscillator_minute,
    optimize_dataframe_memory,
    ensure_json_serializable,
    get_indicator_columns
)


class GetStockTrendMomentumMinuteTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            logging.info(f"GetStockTrendMomentumMinuteTool received parameters: {tool_parameters}")
            
            symbol = tool_parameters.get("symbol", "")
            period = tool_parameters.get("period", "5")
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
            
            # 处理分钟级指标的日期时间格式
            try:
                if len(start_date) == 8:  # YYYYMMDD格式
                    start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]} 09:30:00"
                elif len(start_date) == 10:  # YYYY-MM-DD格式
                    start_date = f"{start_date} 09:30:00"
                
                if len(end_date) == 8:  # YYYYMMDD格式
                    end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]} 15:00:00"
                elif len(end_date) == 10:  # YYYY-MM-DD格式
                    end_date = f"{end_date} 15:00:00"
            except Exception:
                pass  # 如果已经是完整格式，保持不变
            
            logging.info(f"Symbol: {symbol}, Period: {period}, StartDate: {start_date}, EndDate: {end_date}, Adjust: {adjust}")
            
            if not symbol:
                yield self.create_text_message("股票代码不能为空")
                yield self.create_json_message({"error": "symbol required"})
                return
            
            # 获取分钟级历史行情数据
            result = safe_ak_call(
                ak.stock_zh_a_hist_min_em,
                retries=retries,
                timeout=timeout,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                period=period,
                adjust=adjust
            )
            
            if result is None or result.empty or len(result.columns) == 0:
                yield self.create_text_message("暂无历史数据，可能是无效的股票代码")
                yield self.create_json_message({"error": "no data returned"})
                return
            
            # 预处理数据
            df = preprocess_data_for_indicators(result)
            
            # 计算趋势动量震荡指标
            df = calculate_trend_momentum_oscillator_minute(df, period)
            
            # 选择输出列
            output_columns = get_indicator_columns("trend_momentum_oscillator_minute", period)
            available_columns = [col for col in output_columns if col in df.columns]
            result_df = df[available_columns].copy()
            
            # 优化内存使用
            result_df = optimize_dataframe_memory(result_df)
            
            # 确保时间列是字符串格式
            if '时间' in result_df.columns:
                result_df['时间'] = pd.to_datetime(result_df['时间']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # 确保所有列都是JSON序列化兼容的
            result_df = ensure_json_serializable(result_df)
            
            # 对分钟级数据进行合理限制（按股票分析惯例）
            if '时间' in result_df.columns and len(result_df) > 0:
                result_df['时间'] = pd.to_datetime(result_df['时间'])
                end_date_actual = result_df['时间'].max()
                start_date_actual = result_df['时间'].min()
                user_days = (end_date_actual - start_date_actual).days
                
                # 根据周期调整保留的交易日数
                if period == "1":  # 1分钟
                    default_max_days = 5
                elif period == "5":  # 5分钟
                    default_max_days = 10
                else:  # 15分钟、30分钟、60分钟
                    default_max_days = 15
                
                if user_days > default_max_days * 1.5:
                    start_date_limit = end_date_actual - pd.Timedelta(days=default_max_days * 1.5)
                    result_df = result_df[result_df['时间'] >= start_date_limit].copy()
                
                # 转换回字符串格式
                result_df['时间'] = result_df['时间'].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # 输出结果
            yield from process_dataframe_output(result_df, self)
                
        except Exception as e:
            yield from handle_akshare_error(e, self, f"计算趋势动量震荡指标(分钟)")

