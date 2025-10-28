from collections.abc import Generator
from typing import Any
import pandas as pd

import akshare as ak
from provider.akshare_stockdata import safe_ak_call, build_error_payload
from provider.akshare_registry import get_interface_config
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .common_utils import process_dataframe_output, process_other_output, handle_empty_result, validate_required_params, handle_akshare_error, validate_stock_symbol


class StockIndividualInfoSummaryTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"StockIndividualInfoSummaryTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            symbol = tool_parameters.get("symbol", "")
            start_date = tool_parameters.get("start_date", "")
            end_date = tool_parameters.get("end_date", "")
            start_year = tool_parameters.get("start_year", "")
            date = tool_parameters.get("date", "")
            gdhs_date = tool_parameters.get("gdhs_date", "最新")
            quarter = tool_parameters.get("quarter", "")
            logging.info(f"Interface: {interface}, Symbol: {symbol}, Start Date: {start_date}, End Date: {end_date}, Start Year: {start_year}, Date: {date}, GDHS Date: {gdhs_date}, Quarter: {quarter}")
            
            if not interface:
                yield self.create_text_message("请选择要调用的接口")
                yield self.create_json_message({"error": "interface required", "received_params": tool_parameters})
                return
                
            if not symbol:
                yield self.create_text_message("请提供股票代码")
                yield self.create_json_message({"error": "symbol required", "received_params": tool_parameters})
                return
            
            # 对于需要日期参数的接口，验证日期参数
            date_required_interfaces = ["stock_share_change_cninfo"]
            if interface in date_required_interfaces:
                if not start_date or not end_date:
                    yield self.create_text_message(f"接口 {interface} 需要提供开始日期和结束日期")
                    yield self.create_json_message({"error": "start_date and end_date required for this interface", "received_params": tool_parameters})
                    return
            
            
            else:
                # 对于需要symbol+date参数的接口，验证date参数
                symbol_date_required_interfaces = ["stock_gdfx_free_top_10_em", "stock_gdfx_top_10_em"]
                if interface in symbol_date_required_interfaces:
                    if not date:
                        yield self.create_text_message(f"接口 {interface} 需要提供财报发布季度最后日参数")
                        yield self.create_json_message({"error": "date required for this interface", "received_params": tool_parameters})
                        return
                else:
                    # 对于只需要date参数的接口，验证date参数
                    single_date_required_interfaces = []
                    if interface in single_date_required_interfaces:
                        if not date:
                            yield self.create_text_message(f"接口 {interface} 需要提供财报发布季度最后日参数")
                            yield self.create_json_message({"error": "date required for this interface", "received_params": tool_parameters})
                            return
            
            
            # 验证股票代码格式
            validation_result = None
            for result in validate_stock_symbol(symbol, self):
                if isinstance(result, bool):
                    validation_result = result
                else:
                    yield result
            if validation_result is False:
                return
        except Exception as e:
            logging.error(f"Error in _invoke start: {e}")
            yield self.create_text_message(f"参数处理错误: {e}")
            yield self.create_json_message({"error": f"parameter processing error: {e}"})
            return
        
        # 定义接口配置 - 按A股、港股、美股顺序排列
        interface_configs = {
            # A股相关接口
            "stock_individual_info_em": {
                "fn": ak.stock_individual_info_em,
                "description": "东方财富网-股票信息-指定股票"
            },
            "stock_zyjs_ths": {
                "fn": ak.stock_zyjs_ths,
                "description": "同花顺-主营介绍-指定股票"
            },
            "stock_zygc_em": {
                "fn": ak.stock_zygc_em,
                "description": "东方财富网-主营构成-指定股票"
            },
            "stock_news_em": {
                "fn": ak.stock_news_em,
                "description": "东方财富网-新闻资讯数据-指定股票"
            },
            "stock_profile_cninfo": {
                "fn": ak.stock_profile_cninfo,
                "description": "巨潮资讯-公司概况-指定股票"
            },
            "stock_ipo_summary_cninfo": {
                "fn": ak.stock_ipo_summary_cninfo,
                "description": "巨潮资讯-上市相关资讯-指定股票"
            },
            "stock_share_change_cninfo": {
                "fn": ak.stock_share_change_cninfo,
                "description": "巨潮资讯-数据-公司股本变动"
            },
            "stock_fhps_detail_em": {
                "fn": ak.stock_fhps_detail_em,
                "description": "东方财富网-数据中心-分红送配-分红送配详情"
            },
            "stock_fhps_detail_ths": {
                "fn": ak.stock_fhps_detail_ths,
                "description": "同花顺-分红情况"
            },
            "stock_dividend_cninfo": {
                "fn": ak.stock_dividend_cninfo,
                "description": "巨潮资讯-历史分红-指定股票"
            },
            "stock_research_report_em": {
                "fn": ak.stock_research_report_em,
                "description": "东方财富网-数据中心-研究报告-个股研报"
            },
            "stock_gdfx_free_top_10_em": {
                "fn": ak.stock_gdfx_free_top_10_em,
                "description": "东方财富网-个股-十大流通股东-指定股票、日期(季末)"
            },
            "stock_gdfx_top_10_em": {
                "fn": ak.stock_gdfx_top_10_em,
                "description": "东方财富网-个股-十大股东-指定股票、日期(季末)"
            },
            "stock_fund_stock_holder": {
                "fn": ak.stock_fund_stock_holder,
                "description": "新浪财经-基金持股-指定股票"
            },
            "stock_main_stock_holder": {
                "fn": ak.stock_main_stock_holder,
                "description": "新浪财经-主要股东-指定股票"
            },
            "stock_management_change_ths": {
                "fn": ak.stock_management_change_ths,
                "description": "同花顺-公司高管持股变动-指定股票"
            },
            "stock_shareholder_change_ths": {
                "fn": ak.stock_shareholder_change_ths,
                "description": "同花顺-公司股东持股变动-指定股票"
            },
            "stock_zh_a_gdhs": {
                "fn": ak.stock_zh_a_gdhs,
                "description": "东方财富网-股东户数数据-指定日期"
            },
            "stock_zh_a_gdhs_detail_em": {
                "fn": ak.stock_zh_a_gdhs_detail_em,
                "description": "东方财富网-股东户数详情-指定股票"
            },
            "stock_institute_hold_detail": {
                "fn": ak.stock_institute_hold_detail,
                "description": "新浪财经-机构持股详情-指定股票、报告期"
            },
            "stock_institute_recommend_detail": {
                "fn": ak.stock_institute_recommend_detail,
                "description": "新浪财经-股票评级记录-指定股票"
            },
            "stock_value_em": {
                "fn": ak.stock_value_em,
                "description": "东方财富网-估值分析-指定股票"
            },
            "stock_ipo_info": {
                "fn": ak.stock_ipo_info,
                "description": "新浪财经-新股发行-指定股票"
            },
            "stock_add_stock": {
                "fn": ak.stock_add_stock,
                "description": "新浪财经-股票增发-指定股票"
            },
            "stock_restricted_release_queue_sina": {
                "fn": ak.stock_restricted_release_queue_sina,
                "description": "新浪财经-限售解禁-指定股票"
            }
        }
        
        # 获取接口配置
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"未知的接口: {interface}")
            yield self.create_json_message({"error": f"unknown interface: {interface}"})
            return
        
        try:
            # 网络参数 - 统一处理逻辑
            retries = int(tool_parameters.get("retries", 5))
            timeout_param = tool_parameters.get("timeout")  # 让子进程根据接口类型自动决定超时时间
            timeout = float(timeout_param) if timeout_param is not None else None
            
            # 对于股东分析接口，使用更长的超时时间
            if interface in [
                            "stock_gdfx_top_10_em", "stock_gdfx_free_top_10_em"]:
                if timeout is None or timeout < 900:
                    timeout = 900  # 强制使用15分钟超时
                    logging.info(f"Using extended timeout for shareholder analysis interface: {timeout}s")
            
            logging.info(f"Network params - retries: {retries}, timeout: {timeout}")
            
            # 构建调用参数，对特定接口进行代码格式转换
            call_params = {}
            
            # 对于需要股票代码的接口，添加symbol参数
            symbol_required_interfaces = ["stock_individual_info_em", "stock_zyjs_ths", "stock_zygc_em", "stock_news_em", "stock_profile_cninfo", "stock_ipo_summary_cninfo", "stock_share_change_cninfo", "stock_fhps_detail_em", "stock_fhps_detail_ths", "stock_dividend_cninfo", "stock_research_report_em", "stock_gdfx_free_top_10_em", "stock_gdfx_top_10_em", "stock_fund_stock_holder", "stock_main_stock_holder", "stock_management_change_ths", "stock_shareholder_change_ths", "stock_zh_a_gdhs_detail_em", "stock_institute_hold_detail", "stock_institute_recommend_detail", "stock_value_em", "stock_add_stock", "stock_restricted_release_queue_sina"]
            if interface in symbol_required_interfaces:
                processed_symbol = self._process_symbol_format(symbol, interface)
                call_params["symbol"] = processed_symbol
            
            # 对于支持可选股票代码过滤的接口，添加symbol参数（用于数据过滤）
            optional_symbol_interfaces = ["stock_gdfx_free_holding_analyse_em", "stock_gdfx_holding_analyse_em"]
            if interface in optional_symbol_interfaces and symbol:
                # 这些接口不需要传递symbol参数给AKShare，但需要保存用于后续数据过滤
                pass
            
            # 对于需要start_date和end_date参数的接口，添加日期参数
            date_range_required_interfaces = ["stock_share_change_cninfo"]
            if interface in date_range_required_interfaces:
                call_params["start_date"] = start_date
                call_params["end_date"] = end_date
            
            
            # 对于需要symbol+date参数的接口，添加date参数
            symbol_date_required_interfaces = ["stock_gdfx_free_top_10_em", "stock_gdfx_top_10_em"]
            if interface in symbol_date_required_interfaces:
                call_params["date"] = date
            
            # 对于只需要date参数的接口，添加date参数
            single_date_required_interfaces = []
            if interface in single_date_required_interfaces:
                call_params["date"] = date
            
            # 对于需要股东户数日期参数的接口
            if interface == "stock_zh_a_gdhs":
                call_params["symbol"] = gdhs_date
            
            # 对于使用stock参数而不是symbol参数的接口
            if interface in ["stock_ipo_info", "stock_main_stock_holder"]:
                if "symbol" in call_params:
                    call_params["stock"] = call_params.pop("symbol")
            
            # 对于需要报告期参数的接口（stock_institute_hold_detail）
            if interface == "stock_institute_hold_detail":
                if "symbol" in call_params:
                    # stock_institute_hold_detail 使用 stock 参数（股票代码）和 quarter 参数（报告期）
                    call_params["stock"] = call_params.pop("symbol")
                if quarter:
                    call_params["quarter"] = quarter
            
            logging.info(f"Call params: {call_params}")
            logging.info(f"Function: {config['fn']}")
            logging.info(f"Interface: {interface}, Timeout: {timeout}")
            
            # 调用AKShare接口 - timeout现在仅用于子进程超时控制
            try:
                logging.info(f"About to call safe_ak_call with {call_params}")
                result = safe_ak_call(
                    config["fn"],
                    retries=retries,
                    timeout=timeout,
                    **call_params
                )
                logging.info(f"safe_ak_call completed successfully for {interface}")
            except Exception as e:
                # 检查是否是SSL连接错误
                error_msg = str(e)
                if any(keyword in error_msg for keyword in ["SSLError", "SSL", "HTTPSConnectionPool", "Max retries exceeded"]):
                    yield self.create_text_message(f"网络连接超时：\n\n{error_msg}\n\n这通常是由于以下原因：\n1. 个股数据量较大，需要较长时间获取\n2. 网络连接不稳定或SSL握手失败\n3. 数据源服务器响应较慢\n\n建议：\n1. 稍后重试（数据源可能暂时繁忙）\n2. 检查网络连接稳定性\n3. 尝试其他个股信息接口")
                    yield self.create_json_message({
                        "error": "ssl_timeout_error",
                        "message": "SSL连接超时，个股信息获取失败",
                        "details": error_msg,
                        "suggestion": "稍后重试或尝试其他接口"
                    })
                    return
                elif interface in [] and "Length mismatch" in error_msg:
                    # 针对股东相关接口的特殊错误处理
                    yield self.create_text_message(f"股东数据获取失败：\n\n错误信息：{error_msg}\n\n可能的原因：\n1. 指定日期({date})的数据尚未发布或不存在\n2. 数据源结构发生变化\n3. 网络数据异常\n\n建议：\n1. 尝试使用已过去的季末日期（如20240930、20240630、20240331、20231231）\n2. 稍后重试（数据可能正在更新中）\n3. 使用其他股东相关接口")
                    yield self.create_json_message({
                        "error": "data_unavailable_error",
                        "message": "股东数据不可用",
                        "details": error_msg,
                        "suggestion": "尝试使用历史季末日期或稍后重试",
                        "recommended_dates": ["20240930", "20240630", "20240331", "20231231"]
                    })
                    return
                else:
                    # 使用统一的错误处理机制
                    yield from handle_akshare_error(e, self, f"股票代码: {symbol}, 接口: {interface}", str(timeout))
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
                # 定义全局接口列表（用于数据过滤）
                global_interfaces = []
                
                # 定义大数据量接口列表（需要分块处理）
                large_data_interfaces = []
                
                full_data = tool_parameters.get("full_data", False)
                if interface in global_interfaces and symbol and isinstance(result, pd.DataFrame) and '股票代码' in result.columns and not full_data:
                    result = result[result['股票代码'] == symbol]
                
                
                # 根据接口类型选择不同的处理方式
                if interface in large_data_interfaces:
                    # 大数据量接口使用分块处理
                    from .common_utils import process_large_dataframe_output
                    yield from process_large_dataframe_output(result, self)
                else:
                    # 普通接口使用常规处理
                    yield from process_dataframe_output(result, self)
            else:
                yield from process_other_output(result, self)
                
        except Exception as e:
            import logging
            logging.error(f"StockIndividualInfoSummaryTool error: {e}")
            text, payload = build_error_payload(e)
            yield self.create_text_message(text)
            yield self.create_json_message(payload)
            return
    
    def _analyze_symbol_format(self, symbol: str, interface: str) -> str:
        """分析股票代码格式并提供针对性建议"""
        if not symbol:
            return "股票代码为空"
        
        # 接口与市场对应关系 - 按A股、港股、美股顺序排列
        interface_market_map = {
            # A股相关接口
            "stock_individual_info_em": "A股",
            "stock_zyjs_ths": "A股",
            "stock_zygc_em": "A股",
            "stock_news_em": "A股",
            "stock_profile_cninfo": "A股",
            "stock_ipo_summary_cninfo": "A股",
            "stock_share_change_cninfo": "A股",
            "stock_fhps_detail_em": "A股",
            "stock_fhps_detail_ths": "A股",
            "stock_dividend_cninfo": "A股",
            "stock_research_report_em": "A股",
            "stock_gdfx_free_top_10_em": "A股",
            "stock_gdfx_top_10_em": "A股",
            "stock_fund_stock_holder": "A股",
            "stock_main_stock_holder": "A股",
            "stock_institute_hold_detail": "A股",
            "stock_institute_recommend_detail": "A股",
            "stock_value_em": "A股",
            "stock_management_change_ths": "A股",
            "stock_shareholder_change_ths": "A股",
            "stock_ipo_info": "A股",
            "stock_add_stock": "A股",
            "stock_restricted_release_queue_sina": "A股"
        }
        
        expected_market = interface_market_map.get(interface, "未知")
        
        # 分析股票代码格式
        symbol_upper = symbol.upper()
        
        # 检查是否是A股代码
        if symbol.isdigit() and len(symbol) == 6:
            if symbol.startswith(('60', '68')):
                detected_market = "A股(上交所)"
            elif symbol.startswith(('00', '30')):
                detected_market = "A股(深交所)"
            else:
                detected_market = "A股(未知交易所)"
        elif symbol_upper.startswith(('SH', 'SZ')):
            detected_market = "A股(带市场前缀)"
        # 检查是否是港股代码
        elif symbol.isdigit() and len(symbol) == 5:
            detected_market = "港股"
        elif symbol_upper.startswith('HK'):
            detected_market = "港股(带市场前缀)"
        # 检查是否是美股代码
        elif symbol_upper.isalpha() and len(symbol) <= 5:
            detected_market = "美股"
        else:
            detected_market = "未知格式"
        
        # 生成分析结果
        analysis = f"代码分析：\n- 输入代码：{symbol}\n- 检测到市场：{detected_market}\n- 接口期望市场：{expected_market}"
        
        if detected_market != expected_market:
            if expected_market == "A股":
                analysis += f"\n\n❌ 代码格式不匹配：该接口需要A股代码，但您输入的是{detected_market}代码。\n建议使用：600519、000001、SH600519、SZ000001"
            elif expected_market == "港股":
                analysis += f"\n\n❌ 代码格式不匹配：该接口需要港股代码，但您输入的是{detected_market}代码。\n建议使用：00700、03900、HK00700"
            else:
                analysis += f"\n\n❌ 代码格式不匹配：该接口需要{expected_market}代码，但您输入的是{detected_market}代码。"
        else:
            analysis += f"\n\n✅ 代码格式匹配：{detected_market}代码适用于{expected_market}接口"
        
        return analysis
    
    def _process_symbol_format(self, symbol: str, interface: str) -> str:
        """处理股票代码格式，根据接口要求进行转换"""
        if not symbol:
            return symbol
        
        # 需要带市场前缀的接口
        prefix_required_interfaces = [
            "stock_zygc_em",  # 主营构成需要SH/SZ前缀
        ]
        
        # 需要带市场后缀的接口（如.SZ, .SH）
        suffix_required_interfaces = []
        
        # 需要保持原始格式的接口
        original_format_interfaces = []
        
        # 需要小写市场前缀的接口
        lowercase_prefix_interfaces = [
            "stock_gdfx_free_top_10_em",  # 东方财富十大流通股东，需要sh/sz前缀
            "stock_gdfx_top_10_em"  # 东方财富十大股东，需要sh/sz前缀
        ]
        
        # 处理需要市场后缀的接口
        if interface in suffix_required_interfaces and not any(symbol.upper().endswith(suffix) for suffix in ['.SZ', '.SH', '.HK']):
            # 根据代码判断市场并添加后缀
            if symbol.isdigit() and len(symbol) == 6:
                if symbol.startswith(('60', '68')):
                    return f"{symbol}.SH"
                elif symbol.startswith(('00', '30')):
                    return f"{symbol}.SZ"
        
        # 处理需要保持原始格式的接口
        if interface in original_format_interfaces:
            # 新浪财经接口保持原始6位数字格式，不添加任何前缀或后缀
            return symbol
        
        # 处理需要小写市场前缀的接口
        if interface in lowercase_prefix_interfaces and not any(symbol.lower().startswith(prefix) for prefix in ['sh', 'sz', 'hk']):
            # 东方财富股东分析接口需要小写市场前缀
            if symbol.isdigit() and len(symbol) == 6:
                if symbol.startswith(('60', '68')):
                    return f"sh{symbol}"  # 上交所：sh600004
                elif symbol.startswith(('00', '30')):
                    return f"sz{symbol}"  # 深交所：sz000001
        
        # 如果接口需要前缀且当前代码没有前缀
        if interface in prefix_required_interfaces and not any(symbol.upper().startswith(prefix) for prefix in ['SH', 'SZ', 'HK']):
            # 根据代码判断市场
            if symbol.isdigit() and len(symbol) == 6:
                if symbol.startswith(('60', '68')):
                    return f"SH{symbol}"
                elif symbol.startswith(('00', '30')):
                    return f"SZ{symbol}"
        
        return symbol
    
