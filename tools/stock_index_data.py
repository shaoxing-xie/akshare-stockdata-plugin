from collections.abc import Generator
from typing import Any
import pandas as pd

import akshare as ak
from provider.akshare_stockdata import safe_ak_call, build_error_payload
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .common_utils import (
    process_dataframe_output, 
    process_other_output, 
    handle_empty_result, 
    handle_akshare_error
)
from .stock_comprehensive_technical_indicators import (
    calculate_trend_momentum_oscillator,
    calculate_trend_momentum_oscillator_minute,
    preprocess_data_for_indicators
)


class StockIndexDataTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
            logging.info(f"StockIndexDataTool received parameters: {tool_parameters}")
            
        try:
            # 提取参数
            interface = tool_parameters.get("interface", "")
            symbol = tool_parameters.get("symbol", "")
            index_category = tool_parameters.get("index_category", "沪深重要指数")
            period = tool_parameters.get("period", "daily")
            period_minute = tool_parameters.get("period_minute", "15")
            start_date = tool_parameters.get("start_date", "")
            end_date = tool_parameters.get("end_date", "")
            start_datetime = tool_parameters.get("start_datetime", "")
            end_datetime = tool_parameters.get("end_datetime", "")
            retries = int(tool_parameters.get("retries", 5))
            timeout = float(tool_parameters.get("timeout", 900))
            
            logging.info(f"Interface: {interface}, Symbol: {symbol}, Category: {index_category}, Period: {period}, PeriodMinute: {period_minute}")
            logging.info(f"Date range: {start_date} to {end_date}, Datetime range: {start_datetime} to {end_datetime}")
            
            # 验证必需参数
            if not interface:
                yield self.create_text_message("请选择要调用的接口")
                yield self.create_json_message({"error": "interface required", "received_params": tool_parameters})
                return
                
            # 根据接口类型调用不同的函数
            if interface == "stock_zh_index_spot_sina":
                # 新浪实时行情，不需要参数
                result = safe_ak_call(ak.stock_zh_index_spot_sina, retries=retries, timeout=timeout)
                
            elif interface == "stock_zh_index_spot_em":
                # 东方财富实时行情，需要指数类别参数
                if not index_category:
                    yield self.create_text_message("请选择指数类别")
                    yield self.create_json_message({"error": "index_category required for stock_zh_index_spot_em"})
            return
                result = safe_ak_call(ak.stock_zh_index_spot_em, symbol=index_category, retries=retries, timeout=timeout)
                
            elif interface == "stock_zh_index_daily":
                # 新浪历史数据，需要指数代码（带市场标识）
                if not symbol:
                    yield self.create_text_message("请提供指数代码")
                    yield self.create_json_message({"error": "symbol required", "received_params": tool_parameters})
                    return
                # 新浪接口需要带市场前缀的格式
                if not (symbol.startswith('sh') or symbol.startswith('sz') or symbol.startswith('sh') or symbol.startswith('sz')):
                    yield self.create_text_message(f"指数代码格式错误，新浪接口需要带市场标识（如sh000001、sz399552）")
                    yield self.create_json_message({"error": "Invalid symbol format for Sina interface"})
                    return
                result = safe_ak_call(ak.stock_zh_index_daily, symbol=symbol, retries=retries, timeout=timeout)
                
            elif interface == "stock_zh_index_daily_tx":
                # 腾讯历史数据，需要指数代码（带市场标识）
                if not symbol:
                    yield self.create_text_message("请提供指数代码")
                    yield self.create_json_message({"error": "symbol required", "received_params": tool_parameters})
                    return
                # 腾讯接口需要带市场前缀的格式
                if not (symbol.lower().startswith('sh') or symbol.lower().startswith('sz')):
                    yield self.create_text_message(f"指数代码格式错误，腾讯接口需要带市场标识（如sh000001、sz399552）")
                    yield self.create_json_message({"error": "Invalid symbol format for Tencent interface"})
            return
                result = safe_ak_call(ak.stock_zh_index_daily_tx, symbol=symbol.lower(), retries=retries, timeout=timeout)
        
            elif interface == "stock_zh_index_daily_em":
                # 东方财富历史数据，需要指数代码（带市场标识）、日期范围
            if not symbol:
                yield self.create_text_message("请提供指数代码")
                yield self.create_json_message({"error": "symbol required", "received_params": tool_parameters})
                return
                # 东方财富接口需要带市场前缀的格式
                if not (symbol.lower().startswith('sh') or symbol.lower().startswith('sz')):
                    yield self.create_text_message(f"指数代码格式错误，东方财富接口需要带市场标识（如sh000001、sz399552）")
                    yield self.create_json_message({"error": "Invalid symbol format for East Money interface"})
                    return
                if not start_date or not end_date:
                    yield self.create_text_message("请提供日期范围（开始日期和结束日期）")
                    yield self.create_json_message({"error": "date range required"})
                    return
                result = safe_ak_call(
                    ak.stock_zh_index_daily_em,
                    symbol=symbol.lower(),
                    start_date=start_date,
                    end_date=end_date,
                    retries=retries,
                    timeout=timeout
                )
                
            elif interface == "index_zh_a_hist":
                # 东方财富通用历史数据，需要指数代码（纯数字）、周期、日期范围
                if not symbol:
                    yield self.create_text_message("请提供指数代码")
                    yield self.create_json_message({"error": "symbol required", "received_params": tool_parameters})
                    return
                # 提取纯数字部分
                symbol_digits = "".join(ch for ch in str(symbol) if ch.isdigit())
                if not symbol_digits or len(symbol_digits) != 6:
                    yield self.create_text_message(f"指数代码格式错误，通用历史数据接口需要6位纯数字格式（如000001、399006）")
                    yield self.create_json_message({"error": "Invalid symbol format for general historical interface"})
                    return
                if not start_date or not end_date:
                    yield self.create_text_message("请提供日期范围（开始日期和结束日期）")
                    yield self.create_json_message({"error": "date range required"})
                    return
                result = safe_ak_call(
                    ak.index_zh_a_hist,
                    symbol=symbol_digits,
                    period=period,
                    start_date=start_date,
                    end_date=end_date,
                    retries=retries,
                    timeout=timeout
                )
                
            elif interface == "index_zh_a_hist_min_em":
                # 东方财富分钟数据，需要指数代码（纯数字）、分钟周期、日期时间范围
                if not symbol:
                    yield self.create_text_message("请提供指数代码")
                    yield self.create_json_message({"error": "symbol required", "received_params": tool_parameters})
                    return
                # 提取纯数字部分
                symbol_digits = "".join(ch for ch in str(symbol) if ch.isdigit())
                if not symbol_digits or len(symbol_digits) != 6:
                    yield self.create_text_message(f"指数代码格式错误，分钟数据接口需要6位纯数字格式（如000001、399006）")
                    yield self.create_json_message({"error": "Invalid symbol format for minute data interface"})
                return
                if not start_datetime or not end_datetime:
                    yield self.create_text_message("请提供日期时间范围（开始时间和结束时间）")
                    yield self.create_json_message({"error": "datetime range required"})
                return
                result = safe_ak_call(
                    ak.index_zh_a_hist_min_em,
                    symbol=symbol_digits,
                    period=period_minute,
                    start_date=start_datetime,
                    end_date=end_datetime,
                    retries=retries,
                    timeout=timeout
                )
                
            elif interface == "index_trend_momentum_oscillator":
                # 指数趋势动量震荡指标（日频），使用stock_zh_index_daily_em作为基础数据源
                if not symbol:
                    yield self.create_text_message("请提供指数代码")
                    yield self.create_json_message({"error": "symbol required", "received_params": tool_parameters})
                    return
                # 需要带市场前缀的格式
                if not (symbol.lower().startswith('sh') or symbol.lower().startswith('sz')):
                    yield self.create_text_message(f"指数代码格式错误，需要带市场标识（如sh000001、sz399552）")
                    yield self.create_json_message({"error": "Invalid symbol format"})
                return
                if not start_date or not end_date:
                    yield self.create_text_message("请提供日期范围（开始日期和结束日期）")
                    yield self.create_json_message({"error": "date range required"})
                return
        
                # 获取基础数据
                result = safe_ak_call(
                    ak.stock_zh_index_daily_em,
                    symbol=symbol.lower(),
                    start_date=start_date,
                    end_date=end_date,
                    retries=retries,
                    timeout=timeout
                )
                
                # 处理数据并计算指标
                if isinstance(result, pd.DataFrame) and not result.empty:
                    # 重命名列为中文
                    result.columns = ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额']
                    # 计算趋势动量震荡指标（固定为日频）
                    result = calculate_trend_momentum_oscillator(result, "daily")
                    # 转换日期为字符串格式
                    if '日期' in result.columns:
                        result['日期'] = result['日期'].dt.strftime('%Y-%m-%d')
                    
            elif interface == "index_trend_momentum_oscillator_minute":
                # 指数趋势动量震荡指标（分钟），需要指数代码（纯数字）、分钟周期、日期时间范围
                if not symbol:
                    yield self.create_text_message("请提供指数代码")
                    yield self.create_json_message({"error": "symbol required", "received_params": tool_parameters})
                    return
                # 提取纯数字部分
                symbol_digits = "".join(ch for ch in str(symbol) if ch.isdigit())
                if not symbol_digits or len(symbol_digits) != 6:
                    yield self.create_text_message(f"指数代码格式错误，分钟震荡指标接口需要6位纯数字格式（如000001、399006）")
                    yield self.create_json_message({"error": "Invalid symbol format for minute oscillator interface"})
                    return
                if not start_datetime or not end_datetime:
                    yield self.create_text_message("请提供日期时间范围（开始时间和结束时间）")
                    yield self.create_json_message({"error": "datetime range required"})
                    return
                if not period_minute:
                    yield self.create_text_message("请提供分时周期")
                    yield self.create_json_message({"error": "period_minute required"})
                    return
                
                # 获取基础数据
            result = safe_ak_call(
                    ak.index_zh_a_hist_min_em,
                    symbol=symbol_digits,
                    period=period_minute,
                    start_date=start_datetime,
                    end_date=end_datetime,
                retries=retries,
                    timeout=timeout
                )
                
                # 处理数据并计算指标
                if isinstance(result, pd.DataFrame) and not result.empty:
                    # 预处理数据
                    result = result.copy()
                    # 将时间列转换为datetime
                    if '时间' not in result.columns and len(result.columns) > 0:
                        time_col = result.columns[0]
                        result[time_col] = pd.to_datetime(result[time_col])
                        result = result.rename(columns={time_col: '时间'})
                    # 计算趋势动量震荡指标（分钟频）
                    result = calculate_trend_momentum_oscillator_minute(result, period_minute)
                    # 转换时间为字符串格式
                    if '时间' in result.columns:
                        result['时间'] = result['时间'].dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    result = pd.DataFrame()
                    
            else:
                yield self.create_text_message(f"未知的接口: {interface}")
                yield self.create_json_message({"error": f"unknown interface: {interface}"})
                return
            
            # 处理结果
            if result is None:
                yield from handle_empty_result(self)
                return
            
            # 检查是否为空
            if hasattr(result, 'empty') and result.empty:
                    yield from handle_empty_result(self)
                    return
            
            # 输出处理
            if isinstance(result, pd.DataFrame):
                yield from process_dataframe_output(result, self)
            else:
                yield from process_other_output(result, self)
                
        except Exception as e:
            import logging
            logging.error(f"StockIndexDataTool error: {e}")
                text, payload = build_error_payload(e)
                yield self.create_text_message(text)
                yield self.create_json_message(payload)
            return
    
