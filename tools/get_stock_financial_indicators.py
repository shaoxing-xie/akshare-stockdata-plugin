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


class GetStockFinancialIndicatorsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetStockFinancialIndicatorsTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            symbol = tool_parameters.get("stock_code", "")  # 股票代码
            indicator_ths = tool_parameters.get("indicator_ths", "")  # A股同花顺指标类型
            retries = int(tool_parameters.get("retries", 5))
            timeout = float(tool_parameters.get("timeout", 600))
            
            logging.info(f"Interface: {interface}, Symbol: {symbol}, IndicatorTHS: {indicator_ths}, Retries: {retries}, Timeout: {timeout}")
            
            if not interface:
                yield self.create_text_message("请选择要调用的接口")
                yield self.create_json_message({"error": "interface required", "received_params": tool_parameters})
                return
                
        except Exception as e:
            logging.error(f"Error in _invoke start: {e}")
            yield self.create_text_message(f"参数处理错误: {e}")
            yield self.create_json_message({"error": f"parameter processing error: {e}"})
            return
        
        # 定义接口配置 - 完全按照原工具stock_financial_analysis的实现
        interface_configs = {
            "stock_financial_abstract": {
                "fn": ak.stock_financial_abstract,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator": False,
                "requires_start_year": False,
                "timeout": 600,
                "description": "新浪财经-财务报表(关键指标)-指定股票",
                "param_mapping": {"symbol": "symbol"}
            },
            "stock_financial_abstract_ths": {
                "fn": ak.stock_financial_abstract_ths,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator": False,
                "requires_start_year": False,
                "requires_indicator_ths": True,
                "timeout": 600,
                "description": "同花顺-财务指标-主要指标-指定股票、指标类型",
                "param_mapping": {"symbol": "symbol", "indicator": "indicator_ths"}
            },
        }
        
        # 获取接口配置
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"未知的接口: {interface}")
            yield self.create_json_message({"error": f"unknown interface: {interface}"})
            return
        
        # 验证必需参数 - 完全按照原工具stock_financial_analysis的实现
        if config.get("requires_symbol", False) and not symbol:
            yield self.create_text_message("请提供股票代码（如：600519、000001 等）")
            yield self.create_json_message({"error": "symbol required", "received_params": tool_parameters})
            return
        
        if config.get("requires_indicator_ths", False) and not indicator_ths:
            yield self.create_text_message(f"接口 {config['description']} 需要A股同花顺指标类型参数")
            yield self.create_json_message({"error": f"indicator_ths required for {interface}"})
            return
        
        # 验证指标类型是否在允许的范围内
        if config.get("requires_indicator_ths", False) and indicator_ths:
            valid_indicators = config.get("valid_indicators", ["按报告期", "按年度", "按单季度"])
            if indicator_ths not in valid_indicators:
                yield self.create_text_message(f"接口 {config['description']} 不支持指标类型 '{indicator_ths}'。\n\n支持的指标类型：{', '.join(valid_indicators)}")
                yield self.create_json_message({
                    "error": f"invalid indicator type: {indicator_ths}",
                    "valid_indicators": valid_indicators,
                    "received_indicator": indicator_ths
                })
                return
        
        # 股票代码格式验证 - 完全按照原工具stock_financial_analysis的实现
        if config.get("requires_symbol", False) and symbol:
            validation_result = None
            for result in validate_stock_symbol(symbol, self):
                if isinstance(result, bool):
                    validation_result = result
                else:
                    yield result
            if validation_result is False:
                return
        
        # 构建调用参数 - 完全按照原工具stock_financial_analysis的实现
        try:
            call_params = {}
            
            # 根据接口需求添加参数
            if config.get("requires_symbol", False):
                call_params["symbol"] = symbol
            
            if config.get("requires_date", False):
                call_params["date"] = ""  # 此工具不使用date参数
            
            if config.get("requires_indicator", False):
                call_params["indicator"] = ""
            
            if config.get("requires_start_year", False):
                call_params["start_year"] = ""
            
            # 使用参数映射系统（如果存在） - 完全按照原工具stock_financial_analysis的实现
            param_mapping = config.get("param_mapping", {})
            if param_mapping:
                # 清空之前的参数，使用映射系统
                call_params = {}
                for ak_param, tool_param in param_mapping.items():
                    if tool_param == "symbol" and symbol:
                        # 使用注册文件中的预处理逻辑
                        registry_config = get_interface_config(interface)
                        symbol_preprocess = None
                        if registry_config:
                            symbol_preprocess = registry_config.get("params", {}).get("required", {}).get("symbol", {}).get("preprocess")
                        if symbol_preprocess:
                            # 应用预处理
                            if symbol_preprocess == "normalize_symbol_with_uppercase_prefix":
                                call_params[ak_param] = self._normalize_symbol_with_uppercase_prefix(symbol)
                            elif symbol_preprocess == "normalize_symbol":
                                call_params[ak_param] = self._normalize_symbol(symbol)
                            elif symbol_preprocess == "normalize_symbol_with_dot":
                                call_params[ak_param] = self._normalize_symbol_with_dot(symbol)
                            else:
                                call_params[ak_param] = symbol
                        else:
                            call_params[ak_param] = symbol
                    elif tool_param == "indicator_ths" and indicator_ths:
                        # indicator_ths 映射
                        call_params[ak_param] = indicator_ths
                    elif tool_param == "indicator":
                        # 根据接口类型选择正确的indicator参数
                        if config.get("requires_indicator_ths", False) and indicator_ths:
                            call_params[ak_param] = indicator_ths
                    elif tool_param == "start_year":
                        # 此工具不使用start_year
                        pass
            
            # 使用接口特定的超时时间
            interface_timeout = config.get("timeout", timeout)
            
            logging.info(f"Final call params: {call_params}")
            
        except Exception as e:
            logging.error(f"Error in parameter construction: {e}")
            yield self.create_text_message(f"参数构建错误: {e}")
            yield self.create_json_message({"error": f"parameter construction error: {e}"})
            return
        
        # 调用AKShare接口 - 完全按照原工具stock_financial_analysis的实现
        try:
            result = safe_ak_call(
                config["fn"],
                retries=retries,
                timeout=interface_timeout,
                **call_params
            )
            
            if result is None:
                yield self.create_text_message("接口返回空数据")
                yield self.create_json_message({"data": []})
                return
            
            # 处理返回结果
            if isinstance(result, pd.DataFrame):
                if result.empty:
                    yield self.create_text_message("暂无数据")
                    yield self.create_json_message({"data": []})
                else:
                    # 处理DataFrame输出
                    yield from process_dataframe_output(result, self)
            else:
                # 处理其他类型输出
                yield from process_other_output(result, self)
                
        except Exception as e:
            logging.error(f"Error in AKShare call: {e}")
            
            # 检查是否是网络连接错误
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ["ssl", "timeout", "read timed out", "connection", "max retries exceeded", "chunkedencoding", "response ended prematurely"]):
                yield self.create_text_message(f"网络连接中断，请稍后重试\n\n错误详情: {e}")
                yield self.create_json_message({
                    "error": "network_error",
                    "message": "网络连接中断",
                    "details": str(e),
                    "suggestion": "请稍后重试或检查网络连接"
                })
            else:
                # 其他错误
                yield from handle_akshare_error(e, self, f"接口: {interface}, 股票代码: {symbol}, 指标THS: {indicator_ths}", str(interface_timeout))
    
    def _normalize_symbol_with_uppercase_prefix(self, symbol: str) -> str:
        """标准化股票代码，添加大写市场前缀"""
        if not symbol:
            return symbol
        clean_symbol = symbol.replace('SH', '').replace('SZ', '').replace('sh', '').replace('sz', '')
        if clean_symbol.startswith('6'):
            return f"SH{clean_symbol}"
        elif clean_symbol.startswith(('0', '3')):
            return f"SZ{clean_symbol}"
        else:
            return symbol
    
    def _normalize_symbol(self, symbol: str) -> str:
        """标准化股票代码，移除前缀"""
        if not symbol:
            return symbol
        return symbol.replace('SH', '').replace('SZ', '').replace('sh', '').replace('sz', '')
    
    def _normalize_symbol_with_dot(self, symbol: str) -> str:
        """标准化股票代码，添加点号后缀"""
        if not symbol:
            return symbol
        clean_symbol = symbol.replace('SH', '').replace('SZ', '').replace('sh', '').replace('sz', '')
        if clean_symbol.startswith('6'):
            return f"{clean_symbol}.SH"
        elif clean_symbol.startswith(('0', '3')):
            return f"{clean_symbol}.SZ"
        else:
            return symbol
