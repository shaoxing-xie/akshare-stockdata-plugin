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


class GetHsgtIndividualHoldingsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        import logging
        try:
            logging.info(f"GetHsgtIndividualHoldingsTool received parameters: {tool_parameters}")
            
            interface = tool_parameters.get("interface", "")
            symbol = tool_parameters.get("symbol", "")  # 股票代码
            
            logging.info(f"Interface: {interface}, Symbol: {symbol}")
            
            # 验证必需参数
            if not interface:
                yield self.create_text_message("请选择要调用的接口")
                yield self.create_json_message({"error": "interface required", "received_params": tool_parameters})
                return
            
            if not symbol:
                yield self.create_text_message("请提供股票代码（如：600519、000001、00700 等）")
                yield self.create_json_message({"error": "symbol required", "received_params": tool_parameters})
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
            "stock_hsgt_individual_em": {
                "fn": ak.stock_hsgt_individual_em,
                "requires_symbol": True,
                "symbol_type": "individual_stock",  # 个股类
                "requires_market": False,
                "requires_indicator": False,
                "requires_date_range": False,
                "description": "东方财富网-沪深港通持股-具体股票-指定A股和港股"
            },
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
            timeout_param = tool_parameters.get("timeout")  # 让子进程根据接口类型自动决定超时时间
            timeout = float(timeout_param) if timeout_param is not None else None
            logging.info(f"Network params - retries: {retries}, timeout: {timeout} (auto-determined by interface type)")
            
            # 构建调用参数 - 根据接口要求动态构建 - 从原工具迁移
            call_params = {}
            
            # 根据接口要求添加参数 - 从原工具迁移
            if config.get("requires_symbol", False):
                symbol_type = config.get("symbol_type", "")
                if symbol_type == "individual_stock":
                    if not symbol:
                        yield from handle_akshare_error(
                            ValueError("缺少必需参数：股票代码"), 
                            self, 
                            f"接口: {interface}"
                        )
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
                    call_params["symbol"] = symbol
            
            logging.info(f"Call params: {call_params}")
            logging.info(f"Function: {config['fn']}")
            
            # 调用AKShare接口 - timeout现在仅用于子进程超时控制 - 从原工具迁移
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
                if "'noneType' object is not subscriptable" in lower_msg:
                    # 友好提醒：强调检查参数取值是否正确（如股票代码无对应数据）- 从原工具迁移
                    friendly_msg = (
                        "数据源返回为空，无法解析\n\n"
                        "可能原因：\n"
                        "1) 股票代码当前无沪深港通持股数据或代码不存在\n"
                        "2) 数据源暂时不可用或结构变更\n\n"
                        "请检查参数是否正确：\n"
                        "- 股票代码(symbol) 示例：600519、000001、300750\n"
                        "- 可尝试更换股票代码或稍后重试"
                    )
                    yield self.create_text_message(friendly_msg)
                    yield self.create_json_message({
                        "error": "empty_result_or_invalid_parameter",
                        "message": "返回数据为空或参数无效",
                        "details": error_msg,
                        "suggestion": "请核对股票代码是否存在且有沪深港通持股数据，或稍后重试"
                    })
                    return
                # 其他错误 - 从原工具迁移
                yield from handle_akshare_error(e, self, f"接口: {interface}, 股票代码: {symbol}", str(timeout))
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
            logging.error(f"GetHsgtIndividualHoldingsTool error: {e}")
            text, payload = build_error_payload(e)
            yield self.create_text_message(text)
            yield self.create_json_message(payload)
            return

