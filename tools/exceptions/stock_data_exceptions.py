"""
股票数据相关异常定义
提供分层异常处理和详细错误信息
"""
from datetime import datetime
from typing import Dict, Any, Optional
import traceback
import time


class StockDataError(Exception):
    """股票数据相关异常基类"""
    
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
        self.timestamp = datetime.now()
        self.traceback = traceback.format_exc()
    
    def __str__(self):
        return f"[{self.error_code}] {self.message}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'error_type': self.__class__.__name__,
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat(),
            'traceback': self.traceback
        }


class DataFetchError(StockDataError):
    """数据获取异常"""
    
    def __init__(self, message: str, api_name: str = None, symbol: str = None, 
                 retry_count: int = 0, **kwargs):
        super().__init__(message, error_code="DATA_FETCH_ERROR", **kwargs)
        self.api_name = api_name
        self.symbol = symbol
        self.retry_count = retry_count
        
        # 添加特定上下文信息
        if api_name:
            self.details['api_name'] = api_name
        if symbol:
            self.details['symbol'] = symbol
        if retry_count > 0:
            self.details['retry_count'] = retry_count


class DataValidationError(StockDataError):
    """数据验证异常"""
    
    def __init__(self, message: str, validation_type: str = None, 
                 missing_columns: list = None, invalid_data: dict = None, **kwargs):
        super().__init__(message, error_code="DATA_VALIDATION_ERROR", **kwargs)
        self.validation_type = validation_type
        self.missing_columns = missing_columns or []
        self.invalid_data = invalid_data or {}
        
        # 添加验证特定信息
        if validation_type:
            self.details['validation_type'] = validation_type
        if missing_columns:
            self.details['missing_columns'] = missing_columns
        if invalid_data:
            self.details['invalid_data'] = invalid_data


class CalculationError(StockDataError):
    """指标计算异常"""
    
    def __init__(self, message: str, indicator_type: str = None, 
                 calculation_step: str = None, input_data_info: dict = None, **kwargs):
        super().__init__(message, error_code="CALCULATION_ERROR", **kwargs)
        self.indicator_type = indicator_type
        self.calculation_step = calculation_step
        self.input_data_info = input_data_info or {}
        
        # 添加计算特定信息
        if indicator_type:
            self.details['indicator_type'] = indicator_type
        if calculation_step:
            self.details['calculation_step'] = calculation_step
        if input_data_info:
            self.details['input_data_info'] = input_data_info


class ConfigurationError(StockDataError):
    """配置异常"""
    
    def __init__(self, message: str, config_key: str = None, 
                 config_value: Any = None, expected_type: str = None, **kwargs):
        super().__init__(message, error_code="CONFIGURATION_ERROR", **kwargs)
        self.config_key = config_key
        self.config_value = config_value
        self.expected_type = expected_type
        
        # 添加配置特定信息
        if config_key:
            self.details['config_key'] = config_key
        if config_value is not None:
            self.details['config_value'] = str(config_value)
        if expected_type:
            self.details['expected_type'] = expected_type


class TimeoutError(StockDataError):
    """超时异常"""
    
    def __init__(self, message: str, operation: str = None, 
                 timeout_seconds: float = None, **kwargs):
        super().__init__(message, error_code="TIMEOUT_ERROR", **kwargs)
        self.operation = operation
        self.timeout_seconds = timeout_seconds
        
        # 添加超时特定信息
        if operation:
            self.details['operation'] = operation
        if timeout_seconds:
            self.details['timeout_seconds'] = timeout_seconds


class MemoryError(StockDataError):
    """内存异常"""
    
    def __init__(self, message: str, data_size: str = None, 
                 available_memory: str = None, **kwargs):
        super().__init__(message, error_code="MEMORY_ERROR", **kwargs)
        self.data_size = data_size
        self.available_memory = available_memory
        
        # 添加内存特定信息
        if data_size:
            self.details['data_size'] = data_size
        if available_memory:
            self.details['available_memory'] = available_memory


class ErrorContext:
    """错误上下文管理器"""
    
    def __init__(self, operation: str, symbol: str = None, user_id: str = None):
        self.operation = operation
        self.symbol = symbol
        self.user_id = user_id
        self.start_time = time.time()
        self.steps = []
        self.errors = []
    
    def add_step(self, step: str, success: bool = True, details: Dict[str, Any] = None):
        """添加操作步骤"""
        self.steps.append({
            'step': step,
            'success': success,
            'details': details or {},
            'timestamp': time.time(),
            'duration': time.time() - self.start_time
        })
    
    def add_error(self, error: StockDataError):
        """添加错误记录"""
        self.errors.append(error)
    
    def create_error(self, exception_class, message: str, **kwargs):
        """创建带上下文的错误"""
        return exception_class(
            message=message,
            details={
                'operation': self.operation,
                'symbol': self.symbol,
                'user_id': self.user_id,
                'duration': time.time() - self.start_time,
                'steps': self.steps,
                'previous_errors': [e.to_dict() for e in self.errors]
            },
            **kwargs
        )
    
    def get_summary(self) -> Dict[str, Any]:
        """获取上下文摘要"""
        return {
            'operation': self.operation,
            'symbol': self.symbol,
            'user_id': self.user_id,
            'total_duration': time.time() - self.start_time,
            'steps_count': len(self.steps),
            'errors_count': len(self.errors),
            'success_rate': len([s for s in self.steps if s['success']]) / len(self.steps) if self.steps else 0
        }
