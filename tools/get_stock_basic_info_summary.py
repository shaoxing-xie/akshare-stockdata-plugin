from collections.abc import Generator
from typing import Any
import pandas as pd
import logging

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .common_utils import process_dataframe_output, handle_akshare_error
from .stock_comprehensive_technical_indicators import (
    calculate_stock_basic_info_summary,
    ensure_json_serializable
)


class GetStockBasicInfoSummaryTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        try:
            logging.info(f"GetStockBasicInfoSummaryTool received parameters: {tool_parameters}")
            
            symbol = tool_parameters.get("symbol", "")
            retries = int(tool_parameters.get("retries", 5))
            timeout = float(tool_parameters.get("timeout", 600))
            
            logging.info(f"Symbol: {symbol}, Retries: {retries}, Timeout: {timeout}")
            
            if not symbol:
                yield self.create_text_message("股票代码不能为空")
                yield self.create_json_message({"error": "symbol required"})
                return
            
            # 计算个股基本信息汇总
            summary_result = calculate_stock_basic_info_summary(
                symbol, 
                retries, 
                timeout
            )
            
            if "error" in summary_result:
                yield self.create_text_message(f"个股基本信息汇总计算失败: {summary_result['error']}")
                yield self.create_json_message({"error": summary_result['error']})
                return
            
            # 格式化为Markdown表格
            text_output = self._format_basic_info_as_table(summary_result)
            yield self.create_text_message(text_output)
            
            # 输出JSON数据
            yield self.create_json_message({"data": summary_result})
                
        except Exception as e:
            yield from handle_akshare_error(e, self, f"计算个股基本信息汇总")
    
    def _format_basic_info_as_table(self, summary_result: dict) -> str:
        """将基本信息格式化为Markdown表格"""
        try:
            text_output = ""
            
            # 证券资料
            if "证券资料" in summary_result:
                text_output += "### 证券资料\n"
                text_output += "| 项目 | 信息 |\n"
                text_output += "|------|------|\n"
                for key, value in summary_result["证券资料"].items():
                    if value:  # 只显示非空值
                        text_output += f"| {key} | {value} |\n"
                text_output += "\n"
            
            # 公司概况
            if "公司概况" in summary_result:
                text_output += "### 公司概况\n"
                text_output += "| 项目 | 信息 |\n"
                text_output += "|------|------|\n"
                for key, value in summary_result["公司概况"].items():
                    if value:  # 只显示非空值
                        text_output += f"| {key} | {value} |\n"
                text_output += "\n"
            
            # 主营业务
            if "主营业务" in summary_result:
                text_output += "### 主营业务\n"
                text_output += "| 项目 | 信息 |\n"
                text_output += "|------|------|\n"
                for key, value in summary_result["主营业务"].items():
                    if value:  # 只显示非空值
                        text_output += f"| {key} | {value} |\n"
                text_output += "\n"
            
            # 主营业务构成
            if "主营业务构成" in summary_result:
                text_output += "### 主营业务构成\n"
                text_output += "| 项目 | 信息 |\n"
                text_output += "|------|------|\n"
                for key, value in summary_result["主营业务构成"].items():
                    if value:  # 只显示非空值
                        text_output += f"| {key} | {value} |\n"
                text_output += "\n"
            
            return text_output
            
        except Exception as e:
            return f"格式化基本信息失败: {str(e)}"

