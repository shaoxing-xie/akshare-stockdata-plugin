"""
计算器工厂模块
提供各种计算器的创建和管理功能
"""
from typing import Dict, Any, Type, Optional
import logging

from calculators.technical_calculator import TechnicalIndicatorCalculator
from calculators.valuation_calculator import ValuationIndicatorCalculator
from aggregators.basic_info_aggregator import BasicInfoAggregator
from managers.api_manager import APIManager
from processors.data_processor import DataProcessor
from config.indicator_config import ConfigManager


class CalculatorFactory:
    """计算器工厂"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._calculators = {
            'technical': TechnicalIndicatorCalculator,
            'valuation': ValuationIndicatorCalculator,
            'basic_info': BasicInfoAggregator
        }
    
    def create_calculator(self, calculator_type: str, **kwargs) -> Any:
        """创建计算器实例"""
        try:
            if calculator_type not in self._calculators:
                raise ValueError(f"Unknown calculator type: {calculator_type}")
            
            calculator_class = self._calculators[calculator_type]
            return calculator_class(**kwargs)
            
        except Exception as e:
            self.logger.error(f"创建计算器失败 {calculator_type}: {e}")
            raise
    
    def get_available_calculators(self) -> list:
        """获取可用的计算器列表"""
        return list(self._calculators.keys())
    
    def register_calculator(self, name: str, calculator_class: Type):
        """注册新的计算器类型"""
        self._calculators[name] = calculator_class
        self.logger.info(f"注册计算器: {name}")
    
    def unregister_calculator(self, name: str):
        """注销计算器类型"""
        if name in self._calculators:
            del self._calculators[name]
            self.logger.info(f"注销计算器: {name}")


class ServiceContainer:
    """服务容器"""
    
    def __init__(self):
        self._services = {}
        self._singletons = {}
        self.logger = logging.getLogger(__name__)
    
    def register(self, name: str, service_class: Type, singleton: bool = False):
        """注册服务"""
        self._services[name] = (service_class, singleton)
        self.logger.info(f"注册服务: {name} (singleton: {singleton})")
    
    def get(self, name: str, **kwargs) -> Any:
        """获取服务实例"""
        try:
            if name in self._singletons:
                return self._singletons[name]
            
            if name not in self._services:
                raise ValueError(f"Service {name} not registered")
            
            service_class, is_singleton = self._services[name]
            instance = service_class(**kwargs)
            
            if is_singleton:
                self._singletons[name] = instance
            
            return instance
            
        except Exception as e:
            self.logger.error(f"获取服务失败 {name}: {e}")
            raise
    
    def register_all_default_services(self):
        """注册所有默认服务"""
        # 注册单例服务
        self.register('data_processor', DataProcessor, singleton=True)
        self.register('api_manager', APIManager, singleton=True)
        self.register('config_manager', ConfigManager, singleton=True)
        self.register('calculator_factory', CalculatorFactory, singleton=True)
        
        self.logger.info("所有默认服务已注册")
    
    def clear_singletons(self):
        """清除单例实例"""
        self._singletons.clear()
        self.logger.info("单例实例已清除")


# 全局服务容器
container = ServiceContainer()
container.register_all_default_services()
