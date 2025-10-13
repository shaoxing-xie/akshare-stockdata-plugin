from collections.abc import Generator
from typing import Any
import pandas as pd

import akshare as ak
from provider.akshare_stockdata import safe_ak_call, build_error_payload
from provider.akshare_registry import get_interface_config
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .common_utils import process_dataframe_output, process_other_output, handle_empty_result, validate_required_params, handle_akshare_error, validate_stock_symbol


class StockFinancialAnalysisTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        import logging
        try:
            logging.info(f"StockFinancialAnalysisTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            symbol = tool_parameters.get("symbol", "")  # 股票代码
            date = tool_parameters.get("date", "")  # 报告日期
            indicator_ths = tool_parameters.get("indicator_ths", "")  # A股同花顺指标类型
            indicator_hk = tool_parameters.get("indicator_hk", "")  # 港股指标类型
            indicator_us = tool_parameters.get("indicator_us", "")  # 美股指标类型
            start_year = tool_parameters.get("start_year", "")  # 起始年份
            report_type = tool_parameters.get("report_type", "")  # 报表类型
            report_type_sina = tool_parameters.get("report_type_sina", "")  # 新浪报表类型
            retries = int(tool_parameters.get("retries", 5))
            timeout = float(tool_parameters.get("timeout", 600))
            
            logging.info(f"Interface: {interface}, Symbol: {symbol}, Date: {date}, IndicatorTHS: {indicator_ths}, IndicatorHK: {indicator_hk}, IndicatorUS: {indicator_us}, StartYear: {start_year}, ReportType: {report_type}, ReportTypeSina: {report_type_sina}, Retries: {retries}, Timeout: {timeout}")
            
            if not interface:
                yield self.create_text_message("请选择要调用的接口")
                yield self.create_json_message({"error": "interface required", "received_params": tool_parameters})
                return
                
        except Exception as e:
            logging.error(f"Error in _invoke start: {e}")
            yield self.create_text_message(f"参数处理错误: {e}")
            yield self.create_json_message({"error": f"parameter processing error: {e}"})
            return
        
        # 定义接口配置 - 按功能分类
        interface_configs = {
            # 日期类接口（需要date参数）- 业绩快报
            "stock_yjbb_em": {
                "fn": ak.stock_yjbb_em,
                "requires_date": True,
                "requires_symbol": False,
                "requires_indicator": False,
                "requires_start_year": False,
                "timeout": 600,
                "description": "东方财富网-业绩报表",
                "param_mapping": {}
            },
            "stock_yjkb_em": {
                "fn": ak.stock_yjkb_em,
                "requires_date": True,
                "requires_symbol": False,
                "requires_indicator": False,
                "requires_start_year": False,
                "timeout": 600,
                "description": "东方财富网-业绩快报",
                "param_mapping": {}
            },
            "stock_yjyg_em": {
                "fn": ak.stock_yjyg_em,
                "requires_date": True,
                "requires_symbol": False,
                "requires_indicator": False,
                "requires_start_year": False,
                "timeout": 600,
                "description": "东方财富网-业绩预告",
                "param_mapping": {}
            },
            "stock_lrb_em": {
                "fn": ak.stock_lrb_em,
                "requires_date": True,
                "requires_symbol": False,
                "requires_indicator": False,
                "requires_start_year": False,
                "timeout": 600,
                "description": "东方财富网-业绩快报-利润表",
                "param_mapping": {}
            },
            "stock_xjll_em": {
                "fn": ak.stock_xjll_em,
                "requires_date": True,
                "requires_symbol": False,
                "requires_indicator": False,
                "requires_start_year": False,
                "timeout": 600,
                "description": "东方财富网-业绩快报-现金流量表",
                "param_mapping": {}
            },
            "stock_zcfz_em": {
                "fn": ak.stock_zcfz_em,
                "requires_date": True,
                "requires_symbol": False,
                "requires_indicator": False,
                "requires_start_year": False,
                "timeout": 600,
                "description": "东方财富网-业绩快报-资产负债表",
                "param_mapping": {}
            },
            "stock_zcfz_bj_em": {
                "fn": ak.stock_zcfz_bj_em,
                "requires_date": True,
                "requires_symbol": False,
                "requires_indicator": False,
                "requires_start_year": False,
                "timeout": 600,
                "description": "东方财富网-北交所-业绩快报-资产负债表",
                "param_mapping": {}
            },
            # 新浪财务报表接口（需要symbol和report_type_sina参数）
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
            # 财务报表接口（需要symbol参数）
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
            "stock_profit_sheet_by_report_em": {
                "fn": ak.stock_profit_sheet_by_report_em,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator": False,
                "requires_start_year": False,
                "timeout": 600,
                "description": "东方财富网-利润表(按报告期)-指定股票",
                "param_mapping": {"symbol": "symbol"}
            },
            "stock_profit_sheet_by_yearly_em": {
                "fn": ak.stock_profit_sheet_by_yearly_em,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator": False,
                "requires_start_year": False,
                "timeout": 600,
                "description": "东方财富网-利润表(按年度)-指定股票",
                "param_mapping": {"symbol": "symbol"}
            },
            "stock_profit_sheet_by_quarterly_em": {
                "fn": ak.stock_profit_sheet_by_quarterly_em,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator": False,
                "requires_start_year": False,
                "timeout": 600,
                "description": "东方财富网-利润表(按单季度)-指定股票",
                "param_mapping": {"symbol": "symbol"}
            },
            "stock_cash_flow_sheet_by_report_em": {
                "fn": ak.stock_cash_flow_sheet_by_report_em,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator": False,
                "requires_start_year": False,
                "timeout": 600,
                "description": "东方财富网-现金流量表(按报告期)-指定股票",
                "param_mapping": {"symbol": "symbol"}
            },
            "stock_cash_flow_sheet_by_yearly_em": {
                "fn": ak.stock_cash_flow_sheet_by_yearly_em,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator": False,
                "requires_start_year": False,
                "timeout": 600,
                "description": "东方财富网-现金流量表(按年度)-指定股票",
                "param_mapping": {"symbol": "symbol"}
            },
            "stock_cash_flow_sheet_by_quarterly_em": {
                "fn": ak.stock_cash_flow_sheet_by_quarterly_em,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator": False,
                "requires_start_year": False,
                "timeout": 600,
                "description": "东方财富网-现金流量表(按单季度)-指定股票",
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
            "stock_financial_benefit_ths": {
                "fn": ak.stock_financial_benefit_ths,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator": False,
                "requires_start_year": False,
                "requires_report_type": True,
                "timeout": 600,
                "description": "同花顺-个股利润表-指定股票、报告类型",
                "param_mapping": {"symbol": "symbol", "indicator": "report_type"}
            },
            "stock_financial_cash_ths": {
                "fn": ak.stock_financial_cash_ths,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator": False,
                "requires_start_year": False,
                "requires_report_type": True,
                "timeout": 600,
                "description": "同花顺-现金流量表-指定股票、报告类型",
                "param_mapping": {"symbol": "symbol", "indicator": "report_type"}
            },
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
            "stock_financial_analysis_indicator_em": {
                "fn": ak.stock_financial_analysis_indicator_em,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator": True,
                "requires_start_year": False,
                "timeout": 600,
                "description": "东方财富网-A股财务分析(主要指标)-指定股票、报告类型",
                "param_mapping": {"symbol": "symbol", "indicator": "indicator_ths"}
            },
            "stock_financial_analysis_indicator": {
                "fn": ak.stock_financial_analysis_indicator,
                "requires_date": False,
                "requires_symbol": True,
                "requires_indicator": False,
                "requires_start_year": True,
                "timeout": 600,
                "description": "新浪财经-财务分析(财务指标)-指定股票、开始年份",
                "param_mapping": {"symbol": "symbol", "start_year": "start_year"}
            },
            
        }
        
        # 获取接口配置  
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"未知的接口: {interface}")
            yield self.create_json_message({"error": f"unknown interface: {interface}"})
            return
        
        # 参数验证
        try:
            # 验证必需参数
            if config["requires_symbol"] and not symbol:
                yield self.create_text_message(f"接口 {config['description']} 需要股票代码参数")
                yield self.create_json_message({"error": f"symbol required for {interface}"})
                return
                
            if config["requires_date"] and not date:
                yield self.create_text_message(f"接口 {config['description']} 需要报告日期参数")
                yield self.create_json_message({"error": f"date required for {interface}"})
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
                
            if config.get("requires_indicator_hk", False) and not indicator_hk:
                yield self.create_text_message(f"接口 {config['description']} 需要港股指标类型参数")
                yield self.create_json_message({"error": f"indicator_hk required for {interface}"})
                return
                
            if config.get("requires_indicator_us", False) and not indicator_us:
                yield self.create_text_message(f"接口 {config['description']} 需要美股指标类型参数")
                yield self.create_json_message({"error": f"indicator_us required for {interface}"})
                return
                
            if config["requires_start_year"] and not start_year:
                yield self.create_text_message(f"接口 {config['description']} 需要起始年份参数")
                yield self.create_json_message({"error": f"start_year required for {interface}"})
                return
                
            if config.get("requires_report_type", False) and not report_type:
                yield self.create_text_message(f"接口 {config['description']} 需要报表类型参数")
                yield self.create_json_message({"error": f"report_type required for {interface}"})
                return
                
            if config.get("requires_report_type_sina", False) and not report_type_sina:
                yield self.create_text_message(f"接口 {config['description']} 需要新浪报表类型参数")
                yield self.create_json_message({"error": f"report_type_sina required for {interface}"})
                return
            
            # 验证股票代码格式
            if config["requires_symbol"] and symbol:
                validation_result = None
                for result in validate_stock_symbol(symbol, self):
                    if isinstance(result, bool):
                        validation_result = result
                    else:
                        yield result
                if validation_result is False:
                    return
            
            # 验证日期格式
            if config["requires_date"] and date:
                if not self._validate_date_format(date):
                    yield self.create_text_message(f"日期格式不正确，应为YYYYMMDD格式: {date}")
                    yield self.create_json_message({"error": f"invalid date format, should be YYYYMMDD: {date}"})
                    return
            
            # 验证年份格式
            if config["requires_start_year"] and start_year:
                if not self._validate_year_format(start_year):
                    yield self.create_text_message(f"年份格式不正确，应为YYYY格式: {start_year}")
                    yield self.create_json_message({"error": f"invalid year format, should be YYYY: {start_year}"})
                    return
                    
        except Exception as e:
            logging.error(f"Error in parameter validation: {e}")
            yield self.create_text_message(f"参数验证错误: {e}")
            yield self.create_json_message({"error": f"parameter validation error: {e}"})
            return
        
        # 构建调用参数
        try:
            call_params = {}
            
            # 根据接口需求添加参数
            if config["requires_symbol"]:
                call_params["symbol"] = symbol
                
            if config["requires_date"]:
                call_params["date"] = date
                
            if config.get("requires_indicator_ths", False):
                call_params["indicator"] = indicator_ths
            elif config.get("requires_indicator_hk", False):
                call_params["indicator"] = indicator_hk
            elif config.get("requires_indicator_us", False):
                call_params["indicator"] = indicator_us
                
            if config["requires_start_year"]:
                call_params["start_year"] = start_year
                
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
            
            # 使用参数映射系统（如果存在）
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
                    elif tool_param == "indicator_ths" and indicator_ths:
                        # indicator_ths 映射
                        call_params[ak_param] = indicator_ths
                    elif tool_param == "indicator":
                        # 根据接口类型选择正确的indicator参数
                        if config.get("requires_indicator_ths", False) and indicator_ths:
                            call_params[ak_param] = indicator_ths
                        elif config.get("requires_indicator_hk", False) and indicator_hk:
                            call_params[ak_param] = indicator_hk
                        elif config.get("requires_indicator_us", False) and indicator_us:
                            call_params[ak_param] = indicator_us
                    elif tool_param == "start_year" and start_year:
                        call_params[ak_param] = start_year
            
            # 使用接口特定的超时时间
            interface_timeout = config.get("timeout", timeout)
            
            logging.info(f"Final call params: {call_params}")
            
        except Exception as e:
            logging.error(f"Error in parameter construction: {e}")
            yield self.create_text_message(f"参数构建错误: {e}")
            yield self.create_json_message({"error": f"parameter construction error: {e}"})
            return
        
        # 调用AKShare接口
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
                yield from handle_akshare_error(e, self, f"接口: {interface}, 股票代码: {symbol}, 日期: {date}, 指标THS: {indicator_ths}, 指标HK: {indicator_hk}, 指标US: {indicator_us}, 起始年份: {start_year}", str(interface_timeout))
    
    def _validate_date_format(self, date_str: str) -> bool:
        """验证日期格式是否为YYYYMMDD"""
        try:
            if len(date_str) != 8:
                return False
            year = int(date_str[:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])
            
            # 基本范围检查
            if year < 2000 or year > 2030:
                return False
            if month < 1 or month > 12:
                return False
            if day < 1 or day > 31:
                return False
                
            return True
        except (ValueError, IndexError):
            return False
    
    def _normalize_symbol_with_uppercase_prefix(self, symbol: str) -> str:
        """标准化股票代码，添加大写市场前缀"""
        if not symbol:
            return symbol
            
        # 移除现有前缀
        clean_symbol = symbol.replace('SH', '').replace('SZ', '').replace('sh', '').replace('sz', '')
        
        # 根据代码判断市场
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
            
        # 移除现有前缀
        clean_symbol = symbol.replace('SH', '').replace('SZ', '').replace('sh', '').replace('sz', '')
        
        # 根据代码判断市场并添加后缀
        if clean_symbol.startswith('6'):
            return f"{clean_symbol}.SH"
        elif clean_symbol.startswith(('0', '3')):
            return f"{clean_symbol}.SZ"
        else:
            return symbol
    
    def _validate_year_format(self, year_str: str) -> bool:
        """验证年份格式是否为YYYY"""
        try:
            if len(year_str) != 4:
                return False
            year = int(year_str)
            return 2000 <= year <= 2030
        except ValueError:
            return False
