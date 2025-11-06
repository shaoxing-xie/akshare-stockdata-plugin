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
    calculate_trend_momentum_oscillator,
    optimize_dataframe_memory,
    ensure_json_serializable
)


class GetIndexTrendMomentumDailyTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetIndexTrendMomentumDailyTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            symbol = tool_parameters.get("symbol", "")
            start_date = tool_parameters.get("start_date", "")
            end_date = tool_parameters.get("end_date", "")
            retries = int(tool_parameters.get("retries", 5))
            timeout = float(tool_parameters.get("timeout", 900))
            
            logging.info(f"Interface: {interface}, Symbol: {symbol}, StartDate: {start_date}, EndDate: {end_date}, Retries: {retries}, Timeout: {timeout}")
            
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
            "index_trend_momentum_oscillator": {
                "fn": ak.stock_zh_index_daily_em,
                "requires_symbol": True,
                "requires_prefix": True,
                "requires_date_range": True,
                "description": "指数趋势动量震荡指标-指定指数、日期范围"
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
                
                if config.get("requires_prefix"):
                    # 需要带市场前缀的格式
                    if not (symbol.lower().startswith('sh') or symbol.lower().startswith('sz')):
                        yield self.create_text_message(f"指数代码格式错误，需要带市场标识（如sh000001、sz399552）")
                        yield self.create_json_message({"error": "Invalid symbol format, requires prefix"})
                        return
                    call_params["symbol"] = symbol.lower()
            
            # 处理日期范围
            if config.get("requires_date_range"):
                if not start_date or not end_date:
                    yield self.create_text_message("此接口需要日期范围（开始日期和结束日期）")
                    yield self.create_json_message({"error": "date range required for this interface"})
                    return
                call_params["start_date"] = start_date
                call_params["end_date"] = end_date
            
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
                # 重命名列为中文
                result.columns = ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额']
                # 计算趋势动量震荡指标（固定为日频）
                result = calculate_trend_momentum_oscillator(result, "daily")
                # 转换日期为字符串格式
                if '日期' in result.columns:
                    result['日期'] = result['日期'].dt.strftime('%Y-%m-%d')
                
                # 优化内存使用
                result = optimize_dataframe_memory(result)
                
                # 确保所有列都是JSON序列化兼容的
                result = ensure_json_serializable(result)
                
                # 处理DataFrame输出
                yield from process_dataframe_output(result, self)
            else:
                yield from handle_empty_result(self, f"指数代码: {symbol}, 日期范围: {start_date}-{end_date}")
                
        except Exception as e:
            yield from handle_akshare_error(e, self, f"接口: {interface}")

