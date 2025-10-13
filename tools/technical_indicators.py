"""
技术指标计算模块
使用pandas库实现专业级技术指标计算
遵循股票分析领域的标准计算惯例
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import warnings

warnings.filterwarnings('ignore')


class TechnicalIndicators:
    """技术指标计算类"""
    
    @staticmethod
    def calculate_ma(data: pd.DataFrame, periods: List[int] = [5, 10, 20, 30, 60]) -> pd.DataFrame:
        """
        计算移动平均线（MA）
        
        Args:
            data: 包含OHLCV数据的DataFrame
            periods: 移动平均周期列表
            
        Returns:
            添加了MA指标的DataFrame
        """
        try:
            for period in periods:
                data[f'MA{period}'] = data['close'].rolling(window=period, min_periods=1).mean()
            return data
        except Exception as e:
            raise Exception(f"MA指标计算失败: {str(e)}")
    
    @staticmethod
    def calculate_rsi(data: pd.DataFrame, periods: List[int] = [6, 12, 24]) -> pd.DataFrame:
        """
        计算相对强弱指数（RSI）
        
        Args:
            data: 包含OHLCV数据的DataFrame
            periods: RSI周期列表
            
        Returns:
            添加了RSI指标的DataFrame
        """
        try:
            for period in periods:
                delta = data['close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=period, min_periods=1).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=1).mean()
                
                # 避免除零错误
                rs = gain / (loss + 1e-10)
                data[f'RSI{period}'] = 100 - (100 / (1 + rs))
            return data
        except Exception as e:
            raise Exception(f"RSI指标计算失败: {str(e)}")
    
    @staticmethod
    def calculate_macd(data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """
        计算MACD指标
        
        Args:
            data: 包含OHLCV数据的DataFrame
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期
            
        Returns:
            添加了MACD指标的DataFrame
        """
        try:
            ema_fast = data['close'].ewm(span=fast, min_periods=1).mean()
            ema_slow = data['close'].ewm(span=slow, min_periods=1).mean()
            
            data['MACD'] = ema_fast - ema_slow
            data['MACD_Signal'] = data['MACD'].ewm(span=signal, min_periods=1).mean()
            data['MACD_Histogram'] = data['MACD'] - data['MACD_Signal']
            return data
        except Exception as e:
            raise Exception(f"MACD指标计算失败: {str(e)}")
    
    @staticmethod
    def calculate_kdj(data: pd.DataFrame, period: int = 9) -> pd.DataFrame:
        """
        计算KDJ指标
        
        Args:
            data: 包含OHLCV数据的DataFrame
            period: KDJ计算周期
            
        Returns:
            添加了KDJ指标的DataFrame
        """
        try:
            low_min = data['low'].rolling(window=period, min_periods=1).min()
            high_max = data['high'].rolling(window=period, min_periods=1).max()
            
            # 避免除零错误
            rsv = (data['close'] - low_min) / (high_max - low_min + 1e-10) * 100
            
            data['K'] = rsv.ewm(com=2, min_periods=1).mean()
            data['D'] = data['K'].ewm(com=2, min_periods=1).mean()
            data['J'] = 3 * data['K'] - 2 * data['D']
            return data
        except Exception as e:
            raise Exception(f"KDJ指标计算失败: {str(e)}")
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
        """
        计算布林带指标
        
        Args:
            data: 包含OHLCV数据的DataFrame
            period: 布林带周期
            std_dev: 标准差倍数
            
        Returns:
            添加了布林带指标的DataFrame
        """
        try:
            data['BB_Middle'] = data['close'].rolling(window=period, min_periods=1).mean()
            bb_std = data['close'].rolling(window=period, min_periods=1).std()
            
            data['BB_Upper'] = data['BB_Middle'] + (bb_std * std_dev)
            data['BB_Lower'] = data['BB_Middle'] - (bb_std * std_dev)
            return data
        except Exception as e:
            raise Exception(f"布林带指标计算失败: {str(e)}")
    
    @staticmethod
    def calculate_vma(data: pd.DataFrame, periods: List[int] = [5, 10, 20]) -> pd.DataFrame:
        """
        计算成交量移动平均（VMA）
        
        Args:
            data: 包含OHLCV数据的DataFrame
            periods: 成交量移动平均周期列表
            
        Returns:
            添加了VMA指标的DataFrame
        """
        try:
            for period in periods:
                data[f'VMA{period}'] = data['volume'].rolling(window=period, min_periods=1).mean()
            return data
        except Exception as e:
            raise Exception(f"VMA指标计算失败: {str(e)}")
    
    @staticmethod
    def calculate_all_indicators(data: pd.DataFrame, period_type: str = 'daily') -> pd.DataFrame:
        """
        计算所有技术指标
        
        Args:
            data: 包含OHLCV数据的DataFrame
            period_type: 周期类型（daily/minute）
            
        Returns:
            添加了所有技术指标的DataFrame
        """
        try:
            # 确保数据按日期排序
            if 'date' in data.columns:
                data = data.sort_values('date').reset_index(drop=True)
            
            # 确保必要的列存在
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                if col not in data.columns:
                    raise Exception(f"缺少必要的列: {col}")
            
            # 计算各类指标
            data = TechnicalIndicators.calculate_ma(data)
            data = TechnicalIndicators.calculate_rsi(data)
            data = TechnicalIndicators.calculate_macd(data)
            data = TechnicalIndicators.calculate_kdj(data)
            data = TechnicalIndicators.calculate_bollinger_bands(data)
            data = TechnicalIndicators.calculate_vma(data)
            
            return data
            
        except Exception as e:
            raise Exception(f"技术指标计算失败: {str(e)}")
    
    @staticmethod
    def get_indicator_columns() -> List[str]:
        """
        获取所有技术指标列名
        
        Returns:
            技术指标列名列表
        """
        return [
            # MA指标
            'MA5', 'MA10', 'MA20', 'MA30', 'MA60',
            # RSI指标
            'RSI6', 'RSI12', 'RSI24',
            # MACD指标
            'MACD', 'MACD_Signal', 'MACD_Histogram',
            # KDJ指标
            'K', 'D', 'J',
            # 布林带指标
            'BB_Upper', 'BB_Middle', 'BB_Lower',
            # VMA指标
            'VMA5', 'VMA10', 'VMA20'
        ]
    
    @staticmethod
    def validate_data(data: pd.DataFrame) -> bool:
        """
        验证数据格式是否正确
        
        Args:
            data: 要验证的DataFrame
            
        Returns:
            验证结果
        """
        try:
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                if col not in data.columns:
                    return False
                if data[col].isna().all():
                    return False
            return True
        except:
            return False


def calculate_technical_indicators(data: pd.DataFrame, period_type: str = 'daily') -> pd.DataFrame:
    """
    技术指标计算主函数
    
    Args:
        data: 包含OHLCV数据的DataFrame
        period_type: 周期类型（daily/minute）
        
    Returns:
        添加了技术指标的DataFrame
    """
    try:
        # 验证数据
        if not TechnicalIndicators.validate_data(data):
            raise Exception("数据格式不正确，缺少必要的OHLCV列")
        
        # 计算技术指标
        result = TechnicalIndicators.calculate_all_indicators(data, period_type)
        
        return result
        
    except Exception as e:
        raise Exception(f"技术指标计算失败: {str(e)}")


# 测试函数
def test_technical_indicators():
    """测试技术指标计算"""
    try:
        # 创建测试数据
        test_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=100),
            'open': np.random.randn(100).cumsum() + 100,
            'high': np.random.randn(100).cumsum() + 105,
            'low': np.random.randn(100).cumsum() + 95,
            'close': np.random.randn(100).cumsum() + 100,
            'volume': np.random.randint(1000, 10000, 100)
        })
        
        # 计算技术指标
        result = calculate_technical_indicators(test_data, 'daily')
        
        # 检查结果
        indicator_columns = TechnicalIndicators.get_indicator_columns()
        for col in indicator_columns:
            if col in result.columns:
                print(f"✅ {col} 计算成功")
            else:
                print(f"❌ {col} 计算失败")
        
        print("技术指标计算测试完成")
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        return False


if __name__ == "__main__":
    test_technical_indicators()
