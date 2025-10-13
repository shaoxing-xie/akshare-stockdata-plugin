"""
错误处理工具模块
提供错误格式化、日志记录和恢复机制
"""
import logging
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..exceptions.stock_data_exceptions import StockDataError, ErrorContext


class ErrorMessageFormatter:
    """错误信息格式化器"""
    
    @staticmethod
    def format_error(error: StockDataError) -> str:
        """格式化错误信息为用户友好的格式"""
        parts = []
        
        # 基本错误信息
        parts.append(f"❌ {error.message}")
        
        # 错误代码
        if error.error_code:
            parts.append(f"错误代码: {error.error_code}")
        
        # 特定错误类型的详细信息
        if hasattr(error, 'api_name') and error.api_name:
            parts.append(f"API接口: {error.api_name}")
        if hasattr(error, 'symbol') and error.symbol:
            parts.append(f"股票代码: {error.symbol}")
        if hasattr(error, 'validation_type') and error.validation_type:
            parts.append(f"验证类型: {error.validation_type}")
        if hasattr(error, 'indicator_type') and error.indicator_type:
            parts.append(f"指标类型: {error.indicator_type}")
        if hasattr(error, 'retry_count') and error.retry_count > 0:
            parts.append(f"重试次数: {error.retry_count}")
        
        # 错误详情
        if error.details:
            parts.append("详细信息:")
            for key, value in error.details.items():
                if key not in ['api_name', 'symbol', 'validation_type', 'indicator_type', 'retry_count']:
                    parts.append(f"  - {key}: {value}")
        
        # 时间戳
        parts.append(f"发生时间: {error.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(parts)
    
    @staticmethod
    def format_suggestion(error: StockDataError) -> str:
        """生成错误解决建议"""
        suggestions = []
        
        if error.error_code == "DATA_FETCH_ERROR":
            suggestions.extend([
                "💡 解决建议:",
                "1. 检查网络连接是否正常",
                "2. 验证股票代码是否正确",
                "3. 稍后重试，可能是API服务暂时不可用",
                "4. 检查API接口是否有限制",
                "5. 尝试使用不同的复权方式"
            ])
        elif error.error_code == "DATA_VALIDATION_ERROR":
            suggestions.extend([
                "💡 解决建议:",
                "1. 检查输入数据格式是否正确",
                "2. 确认数据是否完整",
                "3. 验证日期范围是否合理",
                "4. 检查必需字段是否存在"
            ])
        elif error.error_code == "CALCULATION_ERROR":
            suggestions.extend([
                "💡 解决建议:",
                "1. 检查数据是否足够计算该指标",
                "2. 验证指标参数是否合理",
                "3. 确认数据质量是否良好",
                "4. 尝试使用默认参数"
            ])
        elif error.error_code == "TIMEOUT_ERROR":
            suggestions.extend([
                "💡 解决建议:",
                "1. 检查网络连接速度",
                "2. 减少数据请求量",
                "3. 增加超时时间设置",
                "4. 稍后重试"
            ])
        elif error.error_code == "MEMORY_ERROR":
            suggestions.extend([
                "💡 解决建议:",
                "1. 减少数据量或时间范围",
                "2. 分批处理数据",
                "3. 关闭其他占用内存的程序",
                "4. 增加系统内存"
            ])
        else:
            suggestions.extend([
                "💡 解决建议:",
                "1. 检查输入参数是否正确",
                "2. 稍后重试",
                "3. 联系技术支持"
            ])
        
        return "\n".join(suggestions) if suggestions else ""
    
    @staticmethod
    def format_technical_details(error: StockDataError) -> str:
        """格式化技术细节（用于调试）"""
        details = []
        
        details.append("🔧 技术详情:")
        details.append(f"异常类型: {type(error).__name__}")
        details.append(f"错误代码: {error.error_code}")
        details.append(f"时间戳: {error.timestamp.isoformat()}")
        
        if error.details:
            details.append("详细信息:")
            for key, value in error.details.items():
                details.append(f"  {key}: {value}")
        
        if hasattr(error, 'traceback') and error.traceback:
            details.append("堆栈跟踪:")
            details.append(error.traceback)
        
        return "\n".join(details)


class ErrorLogger:
    """错误日志记录器"""
    
    def __init__(self, logger_name: str = "stock_comprehensive_indicators"):
        self.logger = logging.getLogger(logger_name)
        self.setup_logging()
    
    def setup_logging(self):
        """设置日志格式"""
        if not self.logger.handlers:  # 避免重复添加处理器
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
            )
            
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logging.INFO)
            self.logger.addHandler(console_handler)
            
            # 文件处理器
            file_handler = logging.FileHandler('stock_indicators_errors.log', encoding='utf-8')
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.ERROR)
            self.logger.addHandler(file_handler)
            
            self.logger.setLevel(logging.INFO)
    
    def log_error(self, error: StockDataError, context: ErrorContext = None):
        """记录错误日志"""
        error_info = {
            'error_type': type(error).__name__,
            'error_code': error.error_code,
            'message': error.message,
            'details': error.details,
            'context': context.get_summary() if context else None,
            'timestamp': error.timestamp.isoformat()
        }
        
        self.logger.error(f"Error occurred: {json.dumps(error_info, ensure_ascii=False, indent=2)}")
    
    def log_warning(self, message: str, context: ErrorContext = None):
        """记录警告日志"""
        context_info = context.get_summary() if context else None
        self.logger.warning(f"Warning: {message}, Context: {context_info}")
    
    def log_info(self, message: str, context: ErrorContext = None):
        """记录信息日志"""
        context_info = context.get_summary() if context else None
        self.logger.info(f"Info: {message}, Context: {context_info}")


class RetryStrategyManager:
    """重试策略管理器"""
    
    def __init__(self):
        self.strategies = {
            'exponential_backoff': self._exponential_backoff,
            'linear_backoff': self._linear_backoff,
            'fixed_interval': self._fixed_interval
        }
    
    def retry_with_strategy(self, func, strategy: str = 'exponential_backoff', 
                          max_retries: int = 3, **kwargs):
        """使用指定策略重试"""
        strategy_func = self.strategies.get(strategy, self._exponential_backoff)
        
        for attempt in range(max_retries + 1):
            try:
                return func(**kwargs)
            except Exception as e:
                if attempt == max_retries:
                    raise e
                
                wait_time = strategy_func(attempt, **kwargs)
                time.sleep(wait_time)
    
    def _exponential_backoff(self, attempt: int, base_delay: float = 1.0, **kwargs):
        """指数退避策略"""
        return base_delay * (2 ** attempt)
    
    def _linear_backoff(self, attempt: int, base_delay: float = 1.0, **kwargs):
        """线性退避策略"""
        return base_delay * (attempt + 1)
    
    def _fixed_interval(self, attempt: int, base_delay: float = 1.0, **kwargs):
        """固定间隔策略"""
        return base_delay


class ErrorRecoveryHandler:
    """错误恢复处理器"""
    
    def __init__(self):
        self.recovery_strategies = {
            'DATA_FETCH_ERROR': self._recover_data_fetch,
            'DATA_VALIDATION_ERROR': self._recover_data_validation,
            'CALCULATION_ERROR': self._recover_calculation,
            'TIMEOUT_ERROR': self._recover_timeout
        }
        self.logger = ErrorLogger()
    
    def attempt_recovery(self, error: StockDataError, context: ErrorContext = None) -> Any:
        """尝试错误恢复"""
        recovery_func = self.recovery_strategies.get(error.error_code)
        if recovery_func:
            try:
                self.logger.log_info(f"Attempting recovery for {error.error_code}")
                return recovery_func(error, context)
            except Exception as recovery_error:
                self.logger.log_error(recovery_error, context)
                return None
        return None
    
    def _recover_data_fetch(self, error: StockDataError, context: ErrorContext = None):
        """数据获取错误恢复"""
        # 这里可以实现具体的恢复逻辑
        # 例如：尝试不同的API参数、使用备用数据源等
        return None
    
    def _recover_data_validation(self, error: StockDataError, context: ErrorContext = None):
        """数据验证错误恢复"""
        # 这里可以实现具体的恢复逻辑
        # 例如：修复数据格式、补充缺失字段等
        return None
    
    def _recover_calculation(self, error: StockDataError, context: ErrorContext = None):
        """计算错误恢复"""
        # 这里可以实现具体的恢复逻辑
        # 例如：使用默认参数、简化计算等
        return None
    
    def _recover_timeout(self, error: StockDataError, context: ErrorContext = None):
        """超时错误恢复"""
        # 这里可以实现具体的恢复逻辑
        # 例如：减少数据量、增加超时时间等
        return None


class ErrorReportGenerator:
    """错误报告生成器"""
    
    def __init__(self):
        self.formatter = ErrorMessageFormatter()
        self.logger = ErrorLogger()
    
    def generate_user_report(self, error: StockDataError, context: ErrorContext = None) -> Dict[str, Any]:
        """生成用户友好的错误报告"""
        return {
            'error_summary': self.formatter.format_error(error),
            'suggestions': self.formatter.format_suggestion(error),
            'technical_details': self.formatter.format_technical_details(error),
            'context_summary': context.get_summary() if context else None,
            'support_info': self._get_support_info(error)
        }
    
    def _get_support_info(self, error: StockDataError) -> Dict[str, str]:
        """获取支持信息"""
        return {
            'error_id': f"ERR_{int(time.time())}_{hash(str(error))}",
            'documentation_url': "https://docs.example.com/troubleshooting",
            'contact_email': "support@example.com",
            'timestamp': error.timestamp.isoformat()
        }
