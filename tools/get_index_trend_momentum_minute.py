from collections.abc import Generator
from typing import Any
import pandas as pd

import akshare as ak
from provider.akshare_stockdata import safe_ak_call
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .common_utils import (
    process_dataframe_output, 
    handle_empty_result, 
    handle_akshare_error
)
from .stock_comprehensive_technical_indicators import (
    calculate_trend_momentum_oscillator_minute,
    optimize_dataframe_memory,
    ensure_json_serializable
)


class GetIndexTrendMomentumMinuteTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetIndexTrendMomentumMinuteTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            symbol = tool_parameters.get("symbol", "")
            period_minute = tool_parameters.get("period_minute", "15")
            start_datetime = tool_parameters.get("start_datetime", "")
            end_datetime = tool_parameters.get("end_datetime", "")
            retries = int(tool_parameters.get("retries", 5))
            timeout = float(tool_parameters.get("timeout", 900))
            
            logging.info(f"Interface: {interface}, Symbol: {symbol}, PeriodMinute: {period_minute}, StartDatetime: {start_datetime}, EndDatetime: {end_datetime}, Retries: {retries}, Timeout: {timeout}")
            
            if not interface:
                yield self.create_text_message("请选择要调用的接口")
                yield self.create_json_message({"error": "interface required", "received_params": tool_parameters})
                return
                
        except Exception as e:
            logging.error(f"Error in _invoke start: {e}")
            yield self.create_text_message(f"参数处理错误: {e}")
            yield self.create_json_message({"error": f"parameter processing error: {e}"})
            return
        
        # 定义接口配置
        interface_configs = {
            "index_trend_momentum_oscillator_minute": {
                "fn": ak.index_zh_a_hist_min_em,
                "requires_symbol": True,
                "requires_digits_only": True,
                "requires_period": True,
                "requires_datetime_range": True,
                "description": "指数趋势动量震荡指标(分钟)-指定指数、周期(分钟)、日期时间范围"
            },
        }
        
        # 获取接口配置
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"不支持的接口: {interface}")
            yield self.create_json_message({"error": f"unsupported interface: {interface}"})
            return
        
        try:
            # 构建调用参数
            call_params = {}
            
            # 处理指数代码
            if config.get("requires_symbol"):
                if not symbol:
                    yield self.create_text_message("此接口需要指数代码参数")
                    yield self.create_json_message({"error": "symbol required for this interface"})
                    return
                
                if config.get("requires_digits_only"):
                    # 提取纯数字部分
                    symbol_digits = "".join(ch for ch in str(symbol) if ch.isdigit())
                    if not symbol_digits or len(symbol_digits) != 6:
                        yield self.create_text_message(f"指数代码格式错误，需要6位纯数字格式（如000001、399006）")
                        yield self.create_json_message({"error": "Invalid symbol format, requires 6 digits"})
                        return
                    call_params["symbol"] = symbol_digits
            
            # 处理分钟周期参数
            if config.get("requires_period"):
                if not period_minute:
                    yield self.create_text_message("此接口需要分钟周期参数")
                    yield self.create_json_message({"error": "period_minute required for this interface"})
                    return
                call_params["period"] = period_minute
            
            # 处理日期时间范围
            if config.get("requires_datetime_range"):
                if not start_datetime or not end_datetime:
                    yield self.create_text_message("此接口需要日期时间范围（开始时间和结束时间）")
                    yield self.create_json_message({"error": "datetime range required for this interface"})
                    return
                call_params["start_date"] = start_datetime
                call_params["end_date"] = end_datetime
            
            # 使用接口特定的超时时间
            interface_timeout = config.get("timeout", timeout)
            
            # 获取基础数据
            result = safe_ak_call(
                config["fn"],
                retries=retries,
                timeout=interface_timeout,
                **call_params
            )
            
            if result is None:
                yield self.create_text_message("接口调用失败，未返回数据")
                yield self.create_json_message({"error": "interface call failed, no data returned"})
                return
            
            # 处理结果并计算指标
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
                
                # 优化内存使用
                result = optimize_dataframe_memory(result)
                
                # 确保所有列都是JSON序列化兼容的
                result = ensure_json_serializable(result)
                
                # 处理DataFrame输出
                yield from process_dataframe_output(result, self)
            else:
                yield from handle_empty_result(self, f"指数代码: {symbol}, 分钟周期: {period_minute}, 日期时间范围: {start_datetime}-{end_datetime}")
                
        except Exception as e:
            yield from handle_akshare_error(e, self, f"接口: {interface}")

