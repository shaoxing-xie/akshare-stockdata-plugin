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
    handle_akshare_error
)


class GetStockPerformanceReportsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetStockPerformanceReportsTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            date = tool_parameters.get("date", "")  # 报告日期
            
            logging.info(f"Interface: {interface}, Date: {date}")
            
            # 验证必需参数
            if not interface:
                yield self.create_text_message("请选择要调用的接口")
                yield self.create_json_message({"error": "interface required", "received_params": tool_parameters})
                return
                
        except Exception as e:
            logging.error(f"Error in _invoke start: {e}")
            yield self.create_text_message(f"参数处理错误: {e}")
            yield self.create_json_message({"error": f"parameter processing error: {e}"})
            return
        
        # 定义接口配置 - 从原工具迁移
        interface_configs = {
            "stock_yjbb_em": {
                "fn": ak.stock_yjbb_em,
                "requires_date": True,
                "description": "东方财富网-业绩报表-指定报告日期"
            },
            "stock_yjkb_em": {
                "fn": ak.stock_yjkb_em,
                "requires_date": True,
                "description": "东方财富网-业绩快报-指定报告日期"
            },
            "stock_yjyg_em": {
                "fn": ak.stock_yjyg_em,
                "requires_date": True,
                "description": "东方财富网-业绩预告-指定报告日期"
            },
            "stock_lrb_em": {
                "fn": ak.stock_lrb_em,
                "requires_date": True,
                "description": "东方财富网-业绩快报-利润表-指定报告日期"
            },
            "stock_xjll_em": {
                "fn": ak.stock_xjll_em,
                "requires_date": True,
                "description": "东方财富网-业绩快报-现金流量表-指定报告日期"
            },
            "stock_zcfz_em": {
                "fn": ak.stock_zcfz_em,
                "requires_date": True,
                "description": "东方财富网-业绩快报-资产负债表-指定报告日期"
            },
            "stock_zcfz_bj_em": {
                "fn": ak.stock_zcfz_bj_em,
                "requires_date": True,
                "description": "东方财富网-北交所-业绩快报-资产负债表-指定报告日期"
            },
        }
        
        # 获取接口配置
        config = interface_configs.get(interface)
        if not config:
            yield self.create_text_message(f"未知的接口: {interface}")
            yield self.create_json_message({"error": f"unknown interface: {interface}"})
            return
        
        # 根据接口配置验证必需参数 - 从原工具迁移
        if config.get("requires_date", False) and not date:
            yield self.create_text_message("请提供报告日期参数（格式：YYYYMMDD，如：20250630）")
            yield self.create_json_message({"error": "date required", "received_params": tool_parameters})
            return
        
        # 验证日期格式 - 从原工具迁移
        if config.get("requires_date", False) and date:
            if not self._validate_date_format(date):
                yield self.create_text_message(f"日期格式不正确，应为YYYYMMDD格式: {date}")
                yield self.create_json_message({"error": f"invalid date format, should be YYYYMMDD: {date}"})
                return
        
        try:
            # 网络参数 - 统一处理逻辑 - 从原工具迁移
            retries = int(tool_parameters.get("retries", 5))
            timeout_param = tool_parameters.get("timeout")
            timeout = float(timeout_param) if timeout_param is not None else None
            logging.info(f"Network params - retries: {retries}, timeout: {timeout}")
            
            # 构建调用参数 - 根据接口要求动态构建 - 从原工具迁移
            call_params = {}
            
            if config.get("requires_date", False) and date:
                call_params["date"] = date
            
            logging.info(f"Call params: {call_params}")
            logging.info(f"Function: {config['fn']}")
            
            # 调用AKShare接口 - 从原工具迁移
            try:
                result = safe_ak_call(
                    config["fn"],
                    retries=retries,
                    timeout=timeout,
                    **call_params
                )
            except Exception as e:
                # 检查是否是已知的AKShare接口问题或网络问题 - 从原工具迁移
                error_msg = str(e)
                lower_msg = error_msg.lower()
                # 网络相关错误统一提示（与其它工具保持一致关键词）
                if any(k in lower_msg for k in ["ssl", "timeout", "read timed out", "connection", "max retries exceeded", "chunkedencoding", "response ended prematurely"]):
                    yield self.create_text_message(f"网络连接中断，请稍后重试\n\n错误详情: {error_msg}")
                    yield self.create_json_message({
                        "error": "network_error",
                        "message": "网络连接中断",
                        "details": error_msg,
                        "suggestion": "请稍后重试或检查网络连接"
                    })
                    return
                # 其他错误 - 从原工具迁移
                yield from handle_akshare_error(e, self, f"接口: {interface}, 报告日期: {date}", str(timeout))
                return
            
            # 处理结果 - 从原工具迁移
            if result is None:
                yield from handle_empty_result(self)
                return
            
            # 检查是否为空
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
            logging.error(f"GetStockPerformanceReportsTool error: {e}")
            text, payload = build_error_payload(e)
            yield self.create_text_message(text)
            yield self.create_json_message(payload)
            return
    
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

