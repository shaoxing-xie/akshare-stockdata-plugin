"""
指标配置管理模块
提供技术指标和估值指标的配置管理功能
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import os
import json


@dataclass
class MovingAverageConfig:
    """移动平均线配置"""
    periods: List[int] = None
    enabled: bool = True
    
    def __post_init__(self):
        if self.periods is None:
            self.periods = [5, 10, 20, 30, 60]


@dataclass
class RSIConfig:
    """RSI配置"""
    periods: List[int] = None
    enabled: bool = True
    
    def __post_init__(self):
        if self.periods is None:
            self.periods = [6, 12, 24]


@dataclass
class MACDConfig:
    """MACD配置"""
    fast_period: int = 12
    slow_period: int = 26
    signal_period: int = 9
    enabled: bool = True


@dataclass
class KDJConfig:
    """KDJ配置"""
    k_period: int = 9
    d_period: int = 3
    j_period: int = 3
    enabled: bool = True


@dataclass
class BollingerBandsConfig:
    """布林带配置"""
    period: int = 20
    std_dev: float = 2.0
    enabled: bool = True


@dataclass
class VolumeConfig:
    """成交量配置"""
    periods: List[int] = None
    enabled: bool = True
    
    def __post_init__(self):
        if self.periods is None:
            self.periods = [5, 10, 20]


@dataclass
class ValuationConfig:
    """估值指标配置"""
    enabled: bool = True
    include_pe: bool = True
    include_pb: bool = True
    include_pcf: bool = True
    include_peg: bool = True
    include_roe: bool = True


@dataclass
class TechnicalIndicatorConfig:
    """技术指标配置总类"""
    moving_averages: MovingAverageConfig = None
    rsi: RSIConfig = None
    macd: MACDConfig = None
    kdj: KDJConfig = None
    bollinger_bands: BollingerBandsConfig = None
    volume: VolumeConfig = None
    
    def __post_init__(self):
        if self.moving_averages is None:
            self.moving_averages = MovingAverageConfig()
        if self.rsi is None:
            self.rsi = RSIConfig()
        if self.macd is None:
            self.macd = MACDConfig()
        if self.kdj is None:
            self.kdj = KDJConfig()
        if self.bollinger_bands is None:
            self.bollinger_bands = BollingerBandsConfig()
        if self.volume is None:
            self.volume = VolumeConfig()


@dataclass
class IndicatorConfig:
    """指标配置总类"""
    technical: TechnicalIndicatorConfig = None
    valuation: ValuationConfig = None
    
    def __post_init__(self):
        if self.technical is None:
            self.technical = TechnicalIndicatorConfig()
        if self.valuation is None:
            self.valuation = ValuationConfig()


# 默认配置
DEFAULT_CONFIG = IndicatorConfig()


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> IndicatorConfig:
        """加载配置"""
        if self.config_file and os.path.exists(self.config_file):
            try:
                return self.load_from_file()
            except Exception as e:
                print(f"加载配置文件失败: {e}，使用默认配置")
                return DEFAULT_CONFIG
        else:
            return DEFAULT_CONFIG
    
    def load_from_file(self) -> IndicatorConfig:
        """从文件加载配置"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        return self._dict_to_config(config_data)
    
    def save_to_file(self, config: IndicatorConfig = None):
        """保存配置到文件"""
        if config is None:
            config = self.config
        
        if self.config_file:
            config_dict = self._config_to_dict(config)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, ensure_ascii=False, indent=2)
    
    def get_indicator_config(self, indicator_type: str) -> Dict[str, Any]:
        """获取特定指标配置"""
        if indicator_type == "trend_momentum_oscillator":
            return {
                'moving_averages': self.config.technical.moving_averages,
                'rsi': self.config.technical.rsi,
                'macd': self.config.technical.macd,
                'kdj': self.config.technical.kdj,
                'bollinger_bands': self.config.technical.bollinger_bands,
                'volume': self.config.technical.volume
            }
        elif indicator_type == "dynamic_valuation_indicators":
            return {
                'valuation': self.config.valuation
            }
        else:
            return {}
    
    def update_config(self, indicator_type: str, **kwargs):
        """更新配置"""
        if indicator_type == "trend_momentum_oscillator":
            for key, value in kwargs.items():
                if hasattr(self.config.technical, key):
                    setattr(self.config.technical, key, value)
        elif indicator_type == "dynamic_valuation_indicators":
            for key, value in kwargs.items():
                if hasattr(self.config.valuation, key):
                    setattr(self.config.valuation, key, value)
    
    def _config_to_dict(self, config: IndicatorConfig) -> Dict[str, Any]:
        """将配置对象转换为字典"""
        result = {}
        
        # 技术指标配置
        result['technical'] = {
            'moving_averages': {
                'periods': config.technical.moving_averages.periods,
                'enabled': config.technical.moving_averages.enabled
            },
            'rsi': {
                'periods': config.technical.rsi.periods,
                'enabled': config.technical.rsi.enabled
            },
            'macd': {
                'fast_period': config.technical.macd.fast_period,
                'slow_period': config.technical.macd.slow_period,
                'signal_period': config.technical.macd.signal_period,
                'enabled': config.technical.macd.enabled
            },
            'kdj': {
                'k_period': config.technical.kdj.k_period,
                'd_period': config.technical.kdj.d_period,
                'j_period': config.technical.kdj.j_period,
                'enabled': config.technical.kdj.enabled
            },
            'bollinger_bands': {
                'period': config.technical.bollinger_bands.period,
                'std_dev': config.technical.bollinger_bands.std_dev,
                'enabled': config.technical.bollinger_bands.enabled
            },
            'volume': {
                'periods': config.technical.volume.periods,
                'enabled': config.technical.volume.enabled
            }
        }
        
        # 估值指标配置
        result['valuation'] = {
            'enabled': config.valuation.enabled,
            'include_pe': config.valuation.include_pe,
            'include_pb': config.valuation.include_pb,
            'include_pcf': config.valuation.include_pcf,
            'include_peg': config.valuation.include_peg,
            'include_roe': config.valuation.include_roe
        }
        
        return result
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> IndicatorConfig:
        """将字典转换为配置对象"""
        technical_config = TechnicalIndicatorConfig()
        valuation_config = ValuationConfig()
        
        # 解析技术指标配置
        if 'technical' in config_dict:
            tech_config = config_dict['technical']
            
            if 'moving_averages' in tech_config:
                ma_config = tech_config['moving_averages']
                technical_config.moving_averages = MovingAverageConfig(
                    periods=ma_config.get('periods', [5, 10, 20, 30, 60]),
                    enabled=ma_config.get('enabled', True)
                )
            
            if 'rsi' in tech_config:
                rsi_config = tech_config['rsi']
                technical_config.rsi = RSIConfig(
                    periods=rsi_config.get('periods', [6, 12, 24]),
                    enabled=rsi_config.get('enabled', True)
                )
            
            if 'macd' in tech_config:
                macd_config = tech_config['macd']
                technical_config.macd = MACDConfig(
                    fast_period=macd_config.get('fast_period', 12),
                    slow_period=macd_config.get('slow_period', 26),
                    signal_period=macd_config.get('signal_period', 9),
                    enabled=macd_config.get('enabled', True)
                )
            
            if 'kdj' in tech_config:
                kdj_config = tech_config['kdj']
                technical_config.kdj = KDJConfig(
                    k_period=kdj_config.get('k_period', 9),
                    d_period=kdj_config.get('d_period', 3),
                    j_period=kdj_config.get('j_period', 3),
                    enabled=kdj_config.get('enabled', True)
                )
            
            if 'bollinger_bands' in tech_config:
                bb_config = tech_config['bollinger_bands']
                technical_config.bollinger_bands = BollingerBandsConfig(
                    period=bb_config.get('period', 20),
                    std_dev=bb_config.get('std_dev', 2.0),
                    enabled=bb_config.get('enabled', True)
                )
            
            if 'volume' in tech_config:
                vol_config = tech_config['volume']
                technical_config.volume = VolumeConfig(
                    periods=vol_config.get('periods', [5, 10, 20]),
                    enabled=vol_config.get('enabled', True)
                )
        
        # 解析估值指标配置
        if 'valuation' in config_dict:
            val_config = config_dict['valuation']
            valuation_config = ValuationConfig(
                enabled=val_config.get('enabled', True),
                include_pe=val_config.get('include_pe', True),
                include_pb=val_config.get('include_pb', True),
                include_pcf=val_config.get('include_pcf', True),
                include_peg=val_config.get('include_peg', True),
                include_roe=val_config.get('include_roe', True)
            )
        
        return IndicatorConfig(technical=technical_config, valuation=valuation_config)
