"""
技术指标计算器模块
提供各种技术指标的计算功能
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging

# 尝试导入技术分析库
try:
    import talib
    USE_TALIB = True
    USE_PANDAS_TA = False
    USE_PANDAS_ONLY = False
except ImportError:
    try:
        import pandas_ta as ta
        USE_TALIB = False
        USE_PANDAS_TA = True
        USE_PANDAS_ONLY = False
    except ImportError:
        USE_TALIB = False
        USE_PANDAS_TA = False
        USE_PANDAS_ONLY = True


class TechnicalIndicatorCalculator:
    """技术指标计算器"""
    
    def __init__(self, use_talib: bool = True, use_pandas_ta: bool = False):
        self.use_talib = use_talib and USE_TALIB
        self.use_pandas_ta = use_pandas_ta and USE_PANDAS_TA
        self.use_pandas_only = not (self.use_talib or self.use_pandas_ta)
        self.logger = logging.getLogger(__name__)
        
        if self.use_pandas_only:
            self.logger.warning("使用pandas内置功能计算技术指标")
    
    def calculate_moving_averages(self, df: pd.DataFrame, periods: List[int]) -> pd.DataFrame:
        """计算移动平均线"""
        try:
            df = df.copy()
            close_values = df['收盘'].astype('float64').fillna(0).values
            
            for period in periods:
                if self.use_talib:
                    df[f'MA{period}'] = talib.SMA(close_values, timeperiod=period)
                elif self.use_pandas_ta:
                    df[f'MA{period}'] = ta.sma(df['收盘'], length=period)
                else:
                    df[f'MA{period}'] = df['收盘'].rolling(window=period).mean()
            
            return df
            
        except Exception as e:
            self.logger.error(f"计算移动平均线失败: {e}")
            return df
    
    def calculate_rsi(self, df: pd.DataFrame, periods: List[int]) -> pd.DataFrame:
        """计算RSI指标"""
        try:
            df = df.copy()
            close_values = df['收盘'].astype('float64').fillna(0).values
            
            for period in periods:
                if self.use_talib:
                    df[f'RSI{period}'] = talib.RSI(close_values, timeperiod=period)
                elif self.use_pandas_ta:
                    df[f'RSI{period}'] = ta.rsi(df['收盘'], length=period)
                else:
                    df[f'RSI{period}'] = self._calculate_rsi_pandas(df['收盘'], period)
            
            return df
            
        except Exception as e:
            self.logger.error(f"计算RSI失败: {e}")
            return df
    
    def calculate_macd(self, df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """计算MACD指标"""
        try:
            df = df.copy()
            close_values = df['收盘'].astype('float64').fillna(0).values
            
            if self.use_talib:
                macd, macd_signal, macd_hist = talib.MACD(close_values, 
                                                        fastperiod=fast, slowperiod=slow, signalperiod=signal)
                df['MACD'] = macd
                df['MACD_SIGNAL'] = macd_signal
                df['MACD_HIST'] = macd_hist
            elif self.use_pandas_ta:
                macd_data = ta.macd(df['收盘'], fast=fast, slow=slow, signal=signal)
                df['MACD'] = macd_data[f'MACD_{fast}_{slow}_{signal}']
                df['MACD_SIGNAL'] = macd_data[f'MACDs_{fast}_{slow}_{signal}']
                df['MACD_HIST'] = macd_data[f'MACDh_{fast}_{slow}_{signal}']
            else:
                ema_fast = df['收盘'].ewm(span=fast).mean()
                ema_slow = df['收盘'].ewm(span=slow).mean()
                df['MACD'] = ema_fast - ema_slow
                df['MACD_SIGNAL'] = df['MACD'].ewm(span=signal).mean()
                df['MACD_HIST'] = df['MACD'] - df['MACD_SIGNAL']
            
            return df
            
        except Exception as e:
            self.logger.error(f"计算MACD失败: {e}")
            return df
    
    def calculate_kdj(self, df: pd.DataFrame, k_period: int = 9, d_period: int = 3, j_period: int = 3) -> pd.DataFrame:
        """计算KDJ指标"""
        try:
            df = df.copy()
            high_values = df['最高'].astype('float64').fillna(0).values
            low_values = df['最低'].astype('float64').fillna(0).values
            close_values = df['收盘'].astype('float64').fillna(0).values
            
            if self.use_talib:
                k, d = talib.STOCH(high_values, low_values, close_values, 
                                 fastk_period=k_period, slowk_period=d_period, slowd_period=d_period)
                df['KDJ_K'] = k
                df['KDJ_D'] = d
                df['KDJ_J'] = 3 * k - 2 * d
            elif self.use_pandas_ta:
                stoch_data = ta.stoch(df['最高'], df['最低'], df['收盘'], k=k_period, d=d_period)
                df['KDJ_K'] = stoch_data[f'STOCHk_{k_period}_{d_period}_{d_period}']
                df['KDJ_D'] = stoch_data[f'STOCHd_{k_period}_{d_period}_{d_period}']
                df['KDJ_J'] = 3 * df['KDJ_K'] - 2 * df['KDJ_D']
            else:
                k, d, j = self._calculate_kdj_pandas(df['最高'], df['最低'], df['收盘'], k_period, d_period)
                df['KDJ_K'] = k
                df['KDJ_D'] = d
                df['KDJ_J'] = j
            
            return df
            
        except Exception as e:
            self.logger.error(f"计算KDJ失败: {e}")
            return df
    
    def calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
        """计算布林带指标"""
        try:
            df = df.copy()
            close_values = df['收盘'].astype('float64').fillna(0).values
            
            if self.use_talib:
                upper, middle, lower = talib.BBANDS(close_values, 
                                                  timeperiod=period, nbdevup=std_dev, nbdevdn=std_dev)
                df['BOLL_UPPER'] = upper
                df['BOLL_MIDDLE'] = middle
                df['BOLL_LOWER'] = lower
            elif self.use_pandas_ta:
                bb_data = ta.bbands(df['收盘'], length=period, std=std_dev)
                df['BOLL_UPPER'] = bb_data[f'BBU_{period}_{std_dev}']
                df['BOLL_MIDDLE'] = bb_data[f'BBM_{period}_{std_dev}']
                df['BOLL_LOWER'] = bb_data[f'BBL_{period}_{std_dev}']
            else:
                middle = df['收盘'].rolling(window=period).mean()
                std = df['收盘'].rolling(window=period).std()
                df['BOLL_MIDDLE'] = middle
                df['BOLL_UPPER'] = middle + (std * std_dev)
                df['BOLL_LOWER'] = middle - (std * std_dev)
            
            return df
            
        except Exception as e:
            self.logger.error(f"计算布林带失败: {e}")
            return df
    
    def calculate_volume_indicators(self, df: pd.DataFrame, periods: List[int]) -> pd.DataFrame:
        """计算成交量指标"""
        try:
            df = df.copy()
            volume_values = df['成交量'].astype('float64').fillna(0).values
            
            for period in periods:
                if self.use_talib:
                    df[f'VMA{period}'] = talib.SMA(volume_values, timeperiod=period)
                elif self.use_pandas_ta:
                    df[f'VMA{period}'] = ta.sma(df['成交量'], length=period)
                else:
                    df[f'VMA{period}'] = df['成交量'].rolling(window=period).mean()
            
            return df
            
        except Exception as e:
            self.logger.error(f"计算成交量指标失败: {e}")
            return df
    
    def calculate_all_indicators(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """计算所有技术指标"""
        try:
            df = df.copy()
            
            # 移动平均线
            if config.get('moving_averages', {}).get('enabled', True):
                periods = config['moving_averages'].get('periods', [5, 10, 20, 30, 60])
                df = self.calculate_moving_averages(df, periods)
            
            # RSI
            if config.get('rsi', {}).get('enabled', True):
                periods = config['rsi'].get('periods', [6, 12, 24])
                df = self.calculate_rsi(df, periods)
            
            # MACD
            if config.get('macd', {}).get('enabled', True):
                fast = config['macd'].get('fast_period', 12)
                slow = config['macd'].get('slow_period', 26)
                signal = config['macd'].get('signal_period', 9)
                df = self.calculate_macd(df, fast, slow, signal)
            
            # KDJ
            if config.get('kdj', {}).get('enabled', True):
                k_period = config['kdj'].get('k_period', 9)
                d_period = config['kdj'].get('d_period', 3)
                j_period = config['kdj'].get('j_period', 3)
                df = self.calculate_kdj(df, k_period, d_period, j_period)
            
            # 布林带
            if config.get('bollinger_bands', {}).get('enabled', True):
                period = config['bollinger_bands'].get('period', 20)
                std_dev = config['bollinger_bands'].get('std_dev', 2.0)
                df = self.calculate_bollinger_bands(df, period, std_dev)
            
            # 成交量指标
            if config.get('volume', {}).get('enabled', True):
                periods = config['volume'].get('periods', [5, 10, 20])
                df = self.calculate_volume_indicators(df, periods)
            
            return df
            
        except Exception as e:
            self.logger.error(f"计算技术指标失败: {e}")
            return df
    
    def _calculate_rsi_pandas(self, prices: pd.Series, window: int) -> pd.Series:
        """使用pandas计算RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.astype('float64')
    
    def _calculate_kdj_pandas(self, high: pd.Series, low: pd.Series, close: pd.Series, 
                             k_period: int, d_period: int) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """使用pandas计算KDJ"""
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        rsv = (close - lowest_low) / (highest_high - lowest_low) * 100
        k = rsv.ewm(com=2).mean()
        d = k.ewm(com=2).mean()
        j = 3 * k - 2 * d
        return k.astype('float64'), d.astype('float64'), j.astype('float64')
