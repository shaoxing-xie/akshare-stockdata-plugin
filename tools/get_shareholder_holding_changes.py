from collections.abc import Generator
from typing import Any
import pandas as pd

import akshare as ak
from provider.akshare_stockdata import safe_ak_call, build_error_payload
from provider.akshare_registry import get_interface_config
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .common_utils import process_dataframe_output, process_other_output, handle_empty_result, validate_required_params, handle_akshare_error, validate_stock_symbol, validate_date_format


class GetShareholderHoldingChangesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetShareholderHoldingChangesTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            symbol = tool_parameters.get("symbol", "")
            start_date = tool_parameters.get("start_date", "")
            end_date = tool_parameters.get("end_date", "")
            date = tool_parameters.get("date", "")
            logging.info(f"Interface: {interface}, Symbol: {symbol}, Start Date: {start_date}, End Date: {end_date}, Date: {date}")
            
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
            symbol_date_required_interfaces = ["stock_gdfx_free_top_10_em", "stock_gdfx_top_10_em"]
            if interface in date_required_interfaces:
                if not start_date or not end_date:
                    yield self.create_text_message(f"接口 {interface} 需要提供开始日期和结束日期")
                    yield self.create_json_message({"error": "start_date and end_date required for this interface", "received_params": tool_parameters})
                    return
                
                # 验证日期格式
                validation_result = None
                for result in validate_date_format(start_date, "YYYYMMDD", self):
                    if isinstance(result, bool):
                        validation_result = result
                    else:
                        yield result
                if validation_result is False:
                    return
                
                validation_result = None
                for result in validate_date_format(end_date, "YYYYMMDD", self):
                    if isinstance(result, bool):
                        validation_result = result
                    else:
                        yield result
                if validation_result is False:
                    return
            
            # 对于需要symbol+date参数的接口，验证date参数
            if interface in symbol_date_required_interfaces:
                if not date:
                    yield self.create_text_message(f"接口 {interface} 需要提供财报发布季度最后日参数")
                    yield self.create_json_message({"error": "date required for this interface", "received_params": tool_parameters})
                    return
                
                # 验证日期格式
                validation_result = None
                for result in validate_date_format(date, "YYYYMMDD", self):
                    if isinstance(result, bool):
                        validation_result = result
                    else:
                        yield result
                if validation_result is False:
                    return
            
            # 验证股票代码格式 - 从原工具迁移
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
        
        # 定义接口配置 - 从原工具迁移
        interface_configs = {
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
            "stock_share_change_cninfo": {
                "fn": ak.stock_share_change_cninfo,
                "description": "巨潮资讯-数据-公司股本变动",
                "requires_date_range": True
            },
            "stock_gdfx_free_top_10_em": {
                "fn": ak.stock_gdfx_free_top_10_em,
                "description": "东方财富网-个股-十大流通股东-指定股票、日期(季末)"
            },
            "stock_gdfx_top_10_em": {
                "fn": ak.stock_gdfx_top_10_em,
                "description": "东方财富网-个股-十大股东-指定股票、日期(季末)"
            },
            "stock_zh_a_gbjg_em": {
                "fn": ak.stock_zh_a_gbjg_em,
                "description": "东方财富网-A股数据-股本结构-指定股票",
                "requires_suffix_format": True  # 需要带市场后缀的格式（如 "603392.SH"）
            }
        }
        
        # 获取接口配置
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"未知的接口: {interface}")
            yield self.create_json_message({"error": f"unknown interface: {interface}"})
            return
        
        try:
            # 网络参数 - 统一处理逻辑 - 从原工具迁移
            retries = int(tool_parameters.get("retries", 5))
            timeout_param = tool_parameters.get("timeout")
            timeout = float(timeout_param) if timeout_param is not None else None
            
            # 对于股东分析接口，使用更长的超时时间
            if interface in ["stock_gdfx_top_10_em", "stock_gdfx_free_top_10_em"]:
                if timeout is None or timeout < 900:
                    timeout = 900  # 强制使用15分钟超时
                    logging.info(f"Using extended timeout for shareholder analysis interface: {timeout}s")
            
            logging.info(f"Network params - retries: {retries}, timeout: {timeout}")
            
            # 构建调用参数 - 从原工具迁移
            call_params = {}
            
            # 处理股票代码格式 - 从原工具迁移
            processed_symbol = self._process_symbol_format(symbol, interface)
            
            # 对于使用stock参数而不是symbol参数的接口 - 从原工具迁移
            if interface in ["stock_main_stock_holder"]:
                call_params["stock"] = processed_symbol
            else:
                call_params["symbol"] = processed_symbol
            
            # 对于需要start_date和end_date参数的接口，添加日期参数
            date_range_required_interfaces = ["stock_share_change_cninfo"]
            if interface in date_range_required_interfaces:
                call_params["start_date"] = start_date
                call_params["end_date"] = end_date
            
            # 对于需要symbol+date参数的接口，添加date参数
            if interface in symbol_date_required_interfaces:
                call_params["date"] = date
            
            logging.info(f"Call params: {call_params}")
            logging.info(f"Function: {config['fn']}")
            logging.info(f"Interface: {interface}, Symbol: {symbol}, Processed Symbol: {processed_symbol}, Date: {date if interface in symbol_date_required_interfaces else 'N/A'}")
            
            # 调用AKShare接口 - 从原工具迁移
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
                logging.error(f"safe_ak_call failed for {interface} with symbol {symbol}: {e}")
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
                elif interface in ["stock_gdfx_top_10_em", "stock_gdfx_free_top_10_em"] and "Length mismatch" in error_msg:
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
                    yield from handle_akshare_error(e, self, f"股票代码: {symbol}, 接口: {interface}", str(timeout))
                    return
            
            # 处理结果 - 从原工具迁移
            if result is None:
                yield from handle_empty_result(self)
                return
            
            if hasattr(result, 'empty') and result.empty:
                yield from handle_empty_result(self)
                return
            
            # 输出处理 - 从原工具迁移
            if isinstance(result, pd.DataFrame):
                yield from process_dataframe_output(result, self)
            else:
                yield from process_other_output(result, self)
                
        except Exception as e:
            import logging
            logging.error(f"GetShareholderHoldingChangesTool error: {e}")
            text, payload = build_error_payload(e)
            yield self.create_text_message(text)
            yield self.create_json_message(payload)
            return
    
    def _process_symbol_format(self, symbol: str, interface: str) -> str:
        """处理股票代码格式，根据接口要求进行转换 - 从原工具迁移"""
        if not symbol:
            return symbol
        
        # 需要带市场后缀的接口（如 "603392.SH"）
        suffix_required_interfaces = [
            "stock_zh_a_gbjg_em"  # 东方财富股本结构接口，需要带市场后缀
        ]
        
        # 需要带市场前缀的接口
        prefix_required_interfaces = []
        
        # 需要小写市场前缀的接口
        lowercase_prefix_interfaces = [
            "stock_gdfx_free_top_10_em",  # 东方财富十大流通股东，需要sh/sz前缀
            "stock_gdfx_top_10_em"  # 东方财富十大股东，需要sh/sz前缀
        ]
        
        # 处理需要带市场后缀的接口（如 "603392.SH"）
        if interface in suffix_required_interfaces:
            # 如果已经有后缀格式，直接返回
            if '.' in symbol and symbol.split('.')[1].upper() in ['SH', 'SZ']:
                return symbol
            # 如果已经有前缀格式，转换为后缀格式
            if symbol.upper().startswith('SH') or symbol.lower().startswith('sh'):
                code = symbol[2:] if len(symbol) > 2 else symbol
                return f"{code}.SH"
            elif symbol.upper().startswith('SZ') or symbol.lower().startswith('sz'):
                code = symbol[2:] if len(symbol) > 2 else symbol
                return f"{code}.SZ"
            # 如果是纯数字，根据代码判断市场
            elif symbol.isdigit() and len(symbol) == 6:
                if symbol.startswith(('60', '68')):
                    return f"{symbol}.SH"  # 上交所：603392.SH
                elif symbol.startswith(('00', '30')):
                    return f"{symbol}.SZ"  # 深交所：000001.SZ
        
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
            if symbol.isdigit() and len(symbol) == 6:
                if symbol.startswith(('60', '68')):
                    return f"SH{symbol}"
                elif symbol.startswith(('00', '30')):
                    return f"SZ{symbol}"
        
        return symbol

