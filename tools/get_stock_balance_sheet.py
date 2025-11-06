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


class GetStockBalanceSheetTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetStockBalanceSheetTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            symbol = tool_parameters.get("stock_code", "")  # 股票代码
            report_type = tool_parameters.get("report_type", "")  # 报告类型（同花顺）
            report_type_sina = tool_parameters.get("report_type_sina", "")  # 新浪报表类型
            retries = int(tool_parameters.get("retries", 5))
            timeout = float(tool_parameters.get("timeout", 600))
            
            logging.info(f"Interface: {interface}, Symbol: {symbol}, ReportType: {report_type}, ReportTypeSina: {report_type_sina}, Retries: {retries}, Timeout: {timeout}")
            
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
            "stock_balance_sheet_by_report_em": {
                "fn": ak.stock_balance_sheet_by_report_em,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator": False,
                "requires_start_year": False,
                "timeout": 600,
                "description": "东方财富网-资产负债表(按报告期)-指定股票",
                "param_mapping": {"symbol": "symbol"}
            },
            "stock_balance_sheet_by_yearly_em": {
                "fn": ak.stock_balance_sheet_by_yearly_em,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator": False,
                "requires_start_year": False,
                "timeout": 600,
                "description": "东方财富网-资产负债表(按年度)-指定股票",
                "param_mapping": {"symbol": "symbol"}
            },
            "stock_financial_debt_ths": {
                "fn": ak.stock_financial_debt_ths,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator": False,
                "requires_start_year": False,
                "requires_report_type": True,
                "timeout": 600,
                "description": "同花顺-资产负债表-指定股票、报告类型",
                "param_mapping": {"symbol": "symbol", "indicator": "report_type"}
            },
            "stock_financial_report_sina": {
                "fn": ak.stock_financial_report_sina,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator": False,
                "requires_start_year": False,
                "requires_report_type_sina": True,
                "timeout": 600,
                "description": "新浪财经-财务报表-三大报表"
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
        
        if config.get("requires_report_type", False) and not report_type:
            yield self.create_text_message("请提供报告类型参数（按年度/按报告期/按单季度）")
            yield self.create_json_message({"error": "report_type required", "received_params": tool_parameters})
            return
        
        if config.get("requires_report_type_sina", False) and not report_type_sina:
            yield self.create_text_message("请提供新浪报表类型参数（资产负债表/利润表/现金流量表）")
            yield self.create_json_message({"error": "report_type_sina required", "received_params": tool_parameters})
            return
        
        # 验证新浪报表类型的有效性
        if config.get("requires_report_type_sina", False) and report_type_sina:
            valid_report_types = ["资产负债表", "利润表", "现金流量表"]
            if report_type_sina not in valid_report_types:
                yield self.create_text_message(f"错误：无效的新浪报表类型 '{report_type_sina}'。\n\n支持的报表类型：{', '.join(valid_report_types)}")
                yield self.create_json_message({"error": "invalid_report_type_sina", "message": f"Invalid report type. Valid options: {', '.join(valid_report_types)}"})
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
            
            if config.get("requires_report_type", False):
                call_params["report_type"] = report_type
            
            if config.get("requires_report_type_sina", False):
                # 新浪财经接口需要特殊处理：stock参数需要带市场标识，symbol参数是报表类型
                if symbol:
                    # 添加市场标识
                    clean_symbol = symbol.replace('SH', '').replace('SZ', '').replace('sh', '').replace('sz', '')
                    if clean_symbol.startswith('6'):
                        call_params["stock"] = f"sh{clean_symbol}"
                    elif clean_symbol.startswith(('0', '3')):
                        call_params["stock"] = f"sz{clean_symbol}"
                    else:
                        call_params["stock"] = symbol
                call_params["symbol"] = report_type_sina
            
            # 使用参数映射系统（如果存在） - 完全按照原工具stock_financial_analysis的实现
            param_mapping = config.get("param_mapping", {})
            if param_mapping:
                # 清空之前的参数，使用映射系统
                call_params = {}
                for ak_param, tool_param in param_mapping.items():
                    if tool_param == "symbol" and symbol:
                        # 使用注册文件中的预处理逻辑
                        registry_config = get_interface_config(interface)
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
                    elif tool_param == "report_type" and report_type:
                        call_params[ak_param] = report_type
                    elif tool_param == "indicator_ths":
                        # 此工具不使用indicator_ths
                        pass
                    elif tool_param == "indicator":
                        # 根据接口类型选择正确的indicator参数
                        if config.get("requires_report_type", False) and report_type:
                            call_params[ak_param] = report_type
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
                    # 对于资产负债表接口，可能返回宽表（列数很多），在序列化时可能导致递归深度问题
                    # 直接使用分块处理，跳过估算步骤，避免clean_nan_values的递归深度问题
                    from .common_utils import process_large_dataframe_output
                    # 检查接口名称或列数，如果是宽表则使用分块处理
                    wide_table_interfaces = ["stock_balance_sheet_by_report_em", "stock_balance_sheet_by_yearly_em", "stock_financial_debt_ths"]
                    if interface in wide_table_interfaces or len(result.columns) > 200:
                        logging.info(f"Interface {interface} returns {len(result.columns)} columns, using chunked processing directly to avoid serialization issues")
                        yield from process_large_dataframe_output(result, self, chunk_size=20)  # 宽表使用更小的块大小
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
            error_type = type(e).__name__
            # 检查错误类型和错误信息
            if (any(keyword in error_str for keyword in ["ssl", "timeout", "read timed out", "connection", "max retries exceeded", "chunkedencoding", "response ended prematurely", "connection closed"]) or 
                "ConnectionClosedError" in error_type or "ConnectionAbortedError" in error_type):
                yield self.create_text_message(f"网络连接中断，请稍后重试\n\n错误详情: {e}\n\n提示：如果是数据量较大的接口（如按年度数据），可能需要更长时间处理，请稍后重试。")
                yield self.create_json_message({
                    "error": "network_error",
                    "message": "网络连接中断",
                    "details": str(e),
                    "suggestion": "请稍后重试或检查网络连接。如果是数据量较大的接口，可能需要更长时间处理。"
                })
            else:
                # 其他错误
                yield from handle_akshare_error(e, self, f"接口: {interface}, 股票代码: {symbol}, 报告类型: {report_type}, 新浪报表类型: {report_type_sina}", str(interface_timeout))
    
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
