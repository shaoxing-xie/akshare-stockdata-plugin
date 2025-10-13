from collections.abc import Generator
from typing import Any, Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
import concurrent.futures
from functools import lru_cache
import time
import logging

import akshare as ak

# 导入新的错误处理模块
from .exceptions import (
    StockDataError, DataFetchError, DataValidationError, 
    CalculationError, TimeoutError, MemoryError, ErrorContext
)
from .error_handlers import (
    ErrorMessageFormatter, ErrorLogger, RetryStrategyManager, 
    ErrorRecoveryHandler, ErrorReportGenerator
)

# 尝试导入技术分析库，如果都不可用则使用pandas内置功能
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
        import logging
        logging.warning("talib not available, using pandas_ta as fallback")
    except ImportError:
        USE_TALIB = False
        USE_PANDAS_TA = False
        USE_PANDAS_ONLY = True
        import logging
        logging.warning("Neither talib nor pandas_ta available, using pandas built-in functions")

from provider.akshare_stockdata import safe_ak_call, build_error_payload
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from .common_utils import process_dataframe_output, process_other_output, handle_empty_result, validate_required_params, validate_date_format, handle_akshare_error


# ==================== 性能优化相关函数 ====================

def optimize_dataframe_memory(df: pd.DataFrame) -> pd.DataFrame:
    """
    优化DataFrame内存使用
    """
    df = df.copy()
    
    # 转换整数类型
    for col in df.select_dtypes(include=['int64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='integer')
    
    # 转换浮点数类型
    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='float')
    
    # 注意：不转换字符串为category类型，因为会导致JSON序列化问题
    # 对于估值指标等包含"N/A"字符串的列，保持object类型以确保JSON序列化正常
    
    return df


def preprocess_data_for_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    预处理数据，避免重复转换
    """
    # 检查 DataFrame 是否为空或没有列
    if df.empty or len(df.columns) == 0:
        raise ValueError("输入数据为空或没有列名，可能是无效的股票代码")
    
    df = df.copy()
    
    # 一次性转换所有数值列
    numeric_columns = ['开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率', '均价']
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # 确保数据按日期/时间排序
    if '日期' in df.columns:
        df['日期'] = pd.to_datetime(df['日期'])
        df = df.sort_values('日期').reset_index(drop=True)
    elif '时间' in df.columns:
        df['时间'] = pd.to_datetime(df['时间'])
        df = df.sort_values('时间').reset_index(drop=True)
    
    return df


@lru_cache(maxsize=128)
def precompute_financial_cache(symbol: str, start_year: str = "2020") -> Dict[int, Dict]:
    """
    预计算财务数据缓存，避免重复计算
    使用LRU缓存机制，避免重复获取相同股票的财务数据
    """
    try:
        financial_data = safe_ak_call(
            ak.stock_financial_analysis_indicator,
            retries=3,
            timeout=300,
            symbol=symbol,
            start_year=start_year
        )
        
        if financial_data is None or financial_data.empty:
            return {}
        
        # 将财务数据日期转换为datetime
        financial_data['日期'] = pd.to_datetime(financial_data['日期'])
        
        # 预处理：获取所有可用的年报数据，按年度分组
        annual_data = financial_data[
            (financial_data['日期'].dt.month == 12) & 
            (financial_data['日期'].dt.day == 31)
        ].sort_values('日期')
        
        if annual_data.empty:
            return {}
        
        # 预计算财务指标缓存
        cache = {}
        for _, financial_row in annual_data.iterrows():
            year = financial_row['日期'].year
            cache[year] = {
                'eps': pd.to_numeric(financial_row['摊薄每股收益(元)'], errors='coerce'),
                'bps': pd.to_numeric(financial_row['每股净资产_调整前(元)'], errors='coerce'),
                'cps': pd.to_numeric(financial_row['每股经营性现金流(元)'], errors='coerce'),
                'w_eps': pd.to_numeric(financial_row['加权每股收益(元)'], errors='coerce'),
                'n_eps': pd.to_numeric(financial_row['扣除非经常性损益后的每股收益(元)'], errors='coerce'),
                'adj_bps': pd.to_numeric(financial_row['每股净资产_调整后(元)'], errors='coerce'),
                'cap_reserve': pd.to_numeric(financial_row['每股资本公积金(元)'], errors='coerce'),
                'undist_profit': pd.to_numeric(financial_row['每股未分配利润(元)'], errors='coerce'),
                'growth_rate': pd.to_numeric(financial_row['净利润增长率(%)'], errors='coerce'),
                'roe': pd.to_numeric(financial_row['净资产收益率(%)'], errors='coerce'),
                'date': financial_row['日期']
            }
        
        return cache
        
    except Exception as e:
        print(f"预计算财务数据缓存失败: {e}")
        return {}


def parallel_basic_info_calls(symbol: str, retries: int = 5, timeout: float = 600) -> Dict[str, Any]:
    """
    并行调用基本信息相关接口
    """
    def call_api(api_func, **kwargs):
        return safe_ak_call(api_func, retries=retries, timeout=timeout, **kwargs)
    
    results = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # 提交所有API调用任务
        futures = {
            'basic_info': executor.submit(call_api, ak.stock_individual_info_em, symbol=symbol),
            'company_info': executor.submit(call_api, ak.stock_profile_cninfo, symbol=symbol),
            'business_info': executor.submit(call_api, ak.stock_zyjs_ths, symbol=symbol),
            'current_price': executor.submit(call_api, ak.stock_bid_ask_em, symbol=symbol)
        }
        
        # 等待所有任务完成
        for name, future in futures.items():
            try:
                results[name] = future.result(timeout=timeout)
            except Exception as e:
                results[name] = None
                print(f"API调用失败 {name}: {e}")
    
    return results


def parallel_financial_data_calls(symbol: str, retries: int = 5, timeout: float = 600) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    """
    并行获取财务数据和当前股价
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # 并行获取财务数据和当前股价
        financial_future = executor.submit(
            safe_ak_call, 
            ak.stock_financial_analysis_indicator,
            retries=retries,
            timeout=timeout,
            symbol=symbol,
            start_year="2020"
        )
        
        price_future = executor.submit(
            safe_ak_call,
            ak.stock_bid_ask_em,
            retries=retries,
            timeout=timeout,
            symbol=symbol
        )
        
        # 等待结果
        try:
            financial_data = financial_future.result(timeout=timeout)
            current_price_data = price_future.result(timeout=timeout)
            return financial_data, current_price_data
        except Exception as e:
            print(f"并行获取财务数据失败: {e}")
            return None, None


def process_large_dataset_in_chunks(df: pd.DataFrame, chunk_size: int = 1000, 
                                  process_func=None) -> pd.DataFrame:
    """
    分批处理大数据集
    """
    if len(df) <= chunk_size:
        return process_func(df) if process_func else df
    
    results = []
    for i in range(0, len(df), chunk_size):
        chunk = df.iloc[i:i+chunk_size].copy()
        if process_func:
            processed_chunk = process_func(chunk)
        else:
            processed_chunk = chunk
        results.append(processed_chunk)
    
    return pd.concat(results, ignore_index=True)


def ensure_json_serializable(df: pd.DataFrame) -> pd.DataFrame:
    """
    确保DataFrame的所有列都是JSON序列化兼容的
    """
    try:
        df = df.copy()
        
        for col in df.columns:
            # 处理category类型
            if df[col].dtype.name == 'category':
                df[col] = df[col].astype(str)
            
            # 处理datetime类型
            if df[col].dtype.name.startswith('datetime'):
                df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # 处理timedelta类型
            if df[col].dtype.name.startswith('timedelta'):
                df[col] = df[col].astype(str)
            
            # 处理numpy类型
            if hasattr(df[col].dtype, 'type'):
                if df[col].dtype.type in [np.integer, np.floating]:
                    # 处理numpy数值类型
                    df[col] = df[col].astype(object)
                    # 将NaN值转换为None以确保JSON序列化
                    df[col] = df[col].where(pd.notna(df[col]), None)
                elif df[col].dtype.type == np.bool_:
                    df[col] = df[col].astype(bool)
                elif df[col].dtype.type == np.object_:
                    # 处理object类型中的特殊值
                    df[col] = df[col].where(pd.notna(df[col]), None)
        
        return df
        
    except Exception as e:
        print(f"JSON序列化兼容性处理失败: {e}")
        return df


# ==================== 原有函数优化 ====================

def calculate_trend_momentum_oscillator(df: pd.DataFrame, period: str = "daily") -> pd.DataFrame:
    """
    计算趋势动量震荡指标(日频)-指定股票代码、周期(日频)
    包括：移动平均线、RSI、MACD、KDJ、布林带、成交量指标
    根据周期调整技术指标参数
    """
    # 检查数据有效性
    if df.empty or len(df.columns) == 0:
        raise ValueError("日频数据为空或没有列名，可能是无效的股票代码")
    
    # 检查必要列是否存在
    required_columns = ['开盘', '收盘', '最高', '最低', '成交量']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"日频数据缺少必要列: {missing_columns}")
    
    # 使用预处理函数优化数据处理
    df = preprocess_data_for_indicators(df)
    
    # 使用统一的股票分析领域标准参数
    # 无论什么时间周期，技术指标参数都保持一致
    ma_periods = [5, 10, 20, 30, 60]  # 移动平均线：MA5、MA10、MA20、MA30、MA60
    rsi_periods = [6, 12, 24]  # RSI指标：RSI6、RSI12、RSI24
    macd_params = (12, 26, 9)  # MACD指标：快线12、慢线26、信号线9
    kdj_params = (9, 3, 3)  # KDJ指标：K值9、D值3、J值3
    boll_params = (20, 2.0)  # 布林带：周期20、标准差2.0
    vma_periods = [5, 10, 20]  # 成交量均线：VMA5、VMA10、VMA20
    
    if USE_TALIB:
        # 使用talib计算技术指标
        # 确保数据是numpy数组且为float64类型，处理缺失值
        close_values = df['收盘'].astype('float64').fillna(0).values
        high_values = df['最高'].astype('float64').fillna(0).values
        low_values = df['最低'].astype('float64').fillna(0).values
        volume_values = df['成交量'].astype('float64').fillna(0).values
        
        # 计算移动平均线（使用统一标准参数）
        for period in ma_periods:
            df[f'MA{period}'] = talib.SMA(close_values, timeperiod=period)
        
        # 计算RSI
        df['RSI6'] = talib.RSI(close_values, timeperiod=6)
        df['RSI12'] = talib.RSI(close_values, timeperiod=12)
        df['RSI24'] = talib.RSI(close_values, timeperiod=24)
        
        # 计算MACD
        macd, signal, hist = talib.MACD(close_values, 
                                       fastperiod=macd_params[0], slowperiod=macd_params[1], signalperiod=macd_params[2])
        df['MACD'] = macd
        df['MACD_SIGNAL'] = signal
        df['MACD_HIST'] = hist
        
        # 计算KDJ
        df['KDJ_K'], df['KDJ_D'] = talib.STOCH(high_values, low_values, close_values, 
                                              fastk_period=kdj_params[0], slowk_period=kdj_params[1], slowd_period=kdj_params[2])
        df['KDJ_J'] = 3 * df['KDJ_K'] - 2 * df['KDJ_D']
        
        # 计算布林带
        upper, middle, lower = talib.BBANDS(close_values, 
                                           timeperiod=boll_params[0], nbdevup=boll_params[1], nbdevdn=boll_params[1])
        df['BOLL_UPPER'] = upper
        df['BOLL_MIDDLE'] = middle
        df['BOLL_LOWER'] = lower
        
        # 计算成交量均线（使用统一标准参数）
        for period in vma_periods:
            df[f'VMA{period}'] = talib.SMA(volume_values, timeperiod=period)
    elif USE_PANDAS_TA:
        # 使用pandas_ta计算技术指标
        # 计算移动平均线（使用动态参数）
        for period in ma_periods:
            if period == 4:
                df['MA4W'] = ta.sma(df['收盘'], length=period)
            elif period == 8:
                df['MA8W'] = ta.sma(df['收盘'], length=period)
            elif period == 16:
                df['MA16W'] = ta.sma(df['收盘'], length=period)
            elif period == 24:
                df['MA24W'] = ta.sma(df['收盘'], length=period)
            elif period == 48:
                df['MA48W'] = ta.sma(df['收盘'], length=period)
            elif period == 3:
                df['MA3M'] = ta.sma(df['收盘'], length=period)
            elif period == 6:
                df['MA6M'] = ta.sma(df['收盘'], length=period)
            elif period == 12:
                df['MA12M'] = ta.sma(df['收盘'], length=period)
            elif period == 24:
                df['MA24M'] = ta.sma(df['收盘'], length=period)
            elif period == 36:
                df['MA36M'] = ta.sma(df['收盘'], length=period)
            else:
                # 日线参数
                if period == 5:
                    df['MA5'] = ta.sma(df['收盘'], length=period)
                elif period == 10:
                    df['MA10'] = ta.sma(df['收盘'], length=period)
                elif period == 20:
                    df['MA20'] = ta.sma(df['收盘'], length=period)
                elif period == 30:
                    df['MA30'] = ta.sma(df['收盘'], length=period)
                elif period == 60:
                    df['MA60'] = ta.sma(df['收盘'], length=period)
        
        # 计算RSI
        df['RSI6'] = ta.rsi(df['收盘'], length=6)
        df['RSI12'] = ta.rsi(df['收盘'], length=12)
        df['RSI24'] = ta.rsi(df['收盘'], length=24)
        
        # 计算MACD
        macd_data = ta.macd(df['收盘'], fast=macd_params[0], slow=macd_params[1], signal=macd_params[2])
        df['MACD'] = macd_data[f'MACD_{macd_params[0]}_{macd_params[1]}_{macd_params[2]}']
        df['MACD_SIGNAL'] = macd_data[f'MACDs_{macd_params[0]}_{macd_params[1]}_{macd_params[2]}']
        df['MACD_HIST'] = macd_data[f'MACDh_{macd_params[0]}_{macd_params[1]}_{macd_params[2]}']
        
        # 计算KDJ
        stoch_data = ta.stoch(df['最高'], df['最低'], df['收盘'], k=kdj_params[0], d=kdj_params[1])
        df['KDJ_K'] = stoch_data[f'STOCHk_{kdj_params[0]}_{kdj_params[1]}_{kdj_params[2]}']
        df['KDJ_D'] = stoch_data[f'STOCHd_{kdj_params[0]}_{kdj_params[1]}_{kdj_params[2]}']
        df['KDJ_J'] = 3 * df['KDJ_K'] - 2 * df['KDJ_D']
        
        # 计算布林带
        bb_data = ta.bbands(df['收盘'], length=boll_params[0], std=boll_params[1])
        df['BOLL_UPPER'] = bb_data[f'BBU_{boll_params[0]}_{boll_params[1]}']
        df['BOLL_MIDDLE'] = bb_data[f'BBM_{boll_params[0]}_{boll_params[1]}']
        df['BOLL_LOWER'] = bb_data[f'BBL_{boll_params[0]}_{boll_params[1]}']
        
        # 计算成交量均线（使用动态参数）
        for period in vma_periods:
            if period == 4:
                df['VMA4W'] = ta.sma(df['成交量'], length=period)
            elif period == 8:
                df['VMA8W'] = ta.sma(df['成交量'], length=period)
            elif period == 16:
                df['VMA16W'] = ta.sma(df['成交量'], length=period)
            elif period == 3:
                df['VMA3M'] = ta.sma(df['成交量'], length=period)
            elif period == 6:
                df['VMA6M'] = ta.sma(df['成交量'], length=period)
            elif period == 12:
                df['VMA12M'] = ta.sma(df['成交量'], length=period)
            else:
                # 日线参数
                if period == 5:
                    df['VMA5'] = ta.sma(df['成交量'], length=period)
                elif period == 10:
                    df['VMA10'] = ta.sma(df['成交量'], length=period)
                elif period == 20:
                    df['VMA20'] = ta.sma(df['成交量'], length=period)
    else:
        # 使用pandas内置功能计算技术指标
        # 确保收盘价是float64类型
        close_prices = df['收盘'].astype('float64')
        high_prices = df['最高'].astype('float64')
        low_prices = df['最低'].astype('float64')
        volume = df['成交量'].astype('float64')
        
        # 计算移动平均线（使用动态参数）
        for period in ma_periods:
            if period == 4:
                df['MA4W'] = close_prices.rolling(window=period).mean()
            elif period == 8:
                df['MA8W'] = close_prices.rolling(window=period).mean()
            elif period == 16:
                df['MA16W'] = close_prices.rolling(window=period).mean()
            elif period == 24:
                df['MA24W'] = close_prices.rolling(window=period).mean()
            elif period == 48:
                df['MA48W'] = close_prices.rolling(window=period).mean()
            elif period == 3:
                df['MA3M'] = close_prices.rolling(window=period).mean()
            elif period == 6:
                df['MA6M'] = close_prices.rolling(window=period).mean()
            elif period == 12:
                df['MA12M'] = close_prices.rolling(window=period).mean()
            elif period == 24:
                df['MA24M'] = close_prices.rolling(window=period).mean()
            elif period == 36:
                df['MA36M'] = close_prices.rolling(window=period).mean()
            else:
                # 日线参数
                if period == 5:
                    df['MA5'] = close_prices.rolling(window=period).mean()
                elif period == 10:
                    df['MA10'] = close_prices.rolling(window=period).mean()
                elif period == 20:
                    df['MA20'] = close_prices.rolling(window=period).mean()
                elif period == 30:
                    df['MA30'] = close_prices.rolling(window=period).mean()
                elif period == 60:
                    df['MA60'] = close_prices.rolling(window=period).mean()
        
        # 计算RSI (简化版本)
        def calculate_rsi(prices, window):
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.astype('float64')
        
        df['RSI6'] = calculate_rsi(close_prices, 6)
        df['RSI12'] = calculate_rsi(close_prices, 12)
        df['RSI24'] = calculate_rsi(close_prices, 24)
        
        # 计算MACD (简化版本)
        ema12 = close_prices.ewm(span=macd_params[0]).mean()
        ema26 = close_prices.ewm(span=macd_params[1]).mean()
        df['MACD'] = (ema12 - ema26).astype('float64')
        df['MACD_SIGNAL'] = df['MACD'].ewm(span=macd_params[2]).mean().astype('float64')
        df['MACD_HIST'] = (df['MACD'] - df['MACD_SIGNAL']).astype('float64')
        
        # 计算KDJ (简化版本)
        def calculate_kdj(high, low, close, k_period=9, d_period=3):
            lowest_low = low.rolling(window=k_period).min()
            highest_high = high.rolling(window=k_period).max()
            rsv = (close - lowest_low) / (highest_high - lowest_low) * 100
            k = rsv.ewm(com=2).mean()
            d = k.ewm(com=2).mean()
            j = 3 * k - 2 * d
            return k.astype('float64'), d.astype('float64'), j.astype('float64')
        
        df['KDJ_K'], df['KDJ_D'], df['KDJ_J'] = calculate_kdj(high_prices, low_prices, close_prices, kdj_params[0], kdj_params[1])
        
        # 计算布林带 (简化版本)
        df['BOLL_MIDDLE'] = close_prices.rolling(window=boll_params[0]).mean().astype('float64')
        std = close_prices.rolling(window=boll_params[0]).std()
        df['BOLL_UPPER'] = (df['BOLL_MIDDLE'] + (std * boll_params[1])).astype('float64')
        df['BOLL_LOWER'] = (df['BOLL_MIDDLE'] - (std * boll_params[1])).astype('float64')
        
        # 计算成交量均线（使用动态参数）
        for period in vma_periods:
            if period == 4:
                df['VMA4W'] = volume.rolling(window=period).mean().astype('float64')
            elif period == 8:
                df['VMA8W'] = volume.rolling(window=period).mean().astype('float64')
            elif period == 16:
                df['VMA16W'] = volume.rolling(window=period).mean().astype('float64')
            elif period == 3:
                df['VMA3M'] = volume.rolling(window=period).mean().astype('float64')
            elif period == 6:
                df['VMA6M'] = volume.rolling(window=period).mean().astype('float64')
            elif period == 12:
                df['VMA12M'] = volume.rolling(window=period).mean().astype('float64')
            else:
                # 日线参数
                if period == 5:
                    df['VMA5'] = volume.rolling(window=period).mean().astype('float64')
                elif period == 10:
                    df['VMA10'] = volume.rolling(window=period).mean().astype('float64')
                elif period == 20:
                    df['VMA20'] = volume.rolling(window=period).mean().astype('float64')
    
    # 处理技术指标中的NaN值 - 对于技术指标，NaN通常表示数据不足，应该保持为NaN而不是0
    # 根据周期构建技术指标列列表
    if period == "weekly":
        technical_columns = ['MA4W', 'MA8W', 'MA16W', 'MA24W', 'MA48W', 'RSI6', 'RSI12', 'RSI24', 
                            'MACD', 'MACD_SIGNAL', 'MACD_HIST', 'KDJ_K', 'KDJ_D', 'KDJ_J',
                            'BOLL_UPPER', 'BOLL_MIDDLE', 'BOLL_LOWER', 'VMA4W', 'VMA8W', 'VMA16W']
    elif period == "monthly":
        technical_columns = ['MA3M', 'MA6M', 'MA12M', 'MA24M', 'MA36M', 'RSI6', 'RSI12', 'RSI24', 
                            'MACD', 'MACD_SIGNAL', 'MACD_HIST', 'KDJ_K', 'KDJ_D', 'KDJ_J',
                            'BOLL_UPPER', 'BOLL_MIDDLE', 'BOLL_LOWER', 'VMA3M', 'VMA6M', 'VMA12M']
    else:
        # 日线参数
        technical_columns = ['MA5', 'MA10', 'MA20', 'MA30', 'MA60', 'RSI6', 'RSI12', 'RSI24', 
                            'MACD', 'MACD_SIGNAL', 'MACD_HIST', 'KDJ_K', 'KDJ_D', 'KDJ_J',
                            'BOLL_UPPER', 'BOLL_MIDDLE', 'BOLL_LOWER', 'VMA5', 'VMA10', 'VMA20']
    
    for col in technical_columns:
        if col in df.columns:
            # 对于技术指标，保持NaN值，不填充为0
            # 这样可以更准确地表示数据不足的情况
            pass
    
    return df


def calculate_trend_momentum_oscillator_minute(df: pd.DataFrame, period: str = "5") -> pd.DataFrame:
    """
    计算趋势动量震荡指标(分钟)-指定股票代码、周期(分钟)
    包括：移动平均线、RSI、MACD、KDJ、布林带、成交量指标
    根据分钟周期调整技术指标参数
    """
    # 检查数据有效性
    if df.empty or len(df.columns) == 0:
        raise ValueError("分钟级数据为空或没有列名，可能是无效的股票代码")
    
    # 检查必要列是否存在
    required_columns = ['开盘', '收盘', '最高', '最低', '成交量']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"分钟级数据缺少必要列: {missing_columns}")
    
    # 使用预处理函数优化数据处理
    df = preprocess_data_for_indicators(df)
    
    # 使用统一的股票分析领域标准参数
    # 无论什么时间周期，技术指标参数都保持一致
    ma_periods = [5, 10, 20, 30, 60]  # 移动平均线：MA5、MA10、MA20、MA30、MA60
    rsi_periods = [6, 12, 24]  # RSI指标：RSI6、RSI12、RSI24
    macd_params = (12, 26, 9)  # MACD指标：快线12、慢线26、信号线9
    kdj_params = (9, 3, 3)  # KDJ指标：K值9、D值3、J值3
    boll_params = (20, 2.0)  # 布林带：周期20、标准差2.0
    vma_periods = [5, 10, 20]  # 成交量均线：VMA5、VMA10、VMA20
    
    if USE_TALIB:
        # 使用talib计算技术指标
        # 确保数据是numpy数组且为float64类型，处理缺失值
        close_values = df['收盘'].astype('float64').fillna(0).values
        high_values = df['最高'].astype('float64').fillna(0).values
        low_values = df['最低'].astype('float64').fillna(0).values
        volume_values = df['成交量'].astype('float64').fillna(0).values
        
        # 计算移动平均线（使用动态参数）
        for period_val in ma_periods:
            df[f'MA{period_val}'] = talib.SMA(close_values, timeperiod=period_val)
        
        # 计算RSI
        df['RSI6'] = talib.RSI(close_values, timeperiod=6)
        df['RSI12'] = talib.RSI(close_values, timeperiod=12)
        df['RSI24'] = talib.RSI(close_values, timeperiod=24)
        
        # 计算MACD
        macd, signal, hist = talib.MACD(close_values, 
                                       fastperiod=macd_params[0], slowperiod=macd_params[1], signalperiod=macd_params[2])
        df['MACD'] = macd
        df['MACD_SIGNAL'] = signal
        df['MACD_HIST'] = hist
        
        # 计算KDJ
        df['KDJ_K'], df['KDJ_D'] = talib.STOCH(high_values, low_values, close_values, 
                                              fastk_period=kdj_params[0], slowk_period=kdj_params[1], slowd_period=kdj_params[2])
        df['KDJ_J'] = 3 * df['KDJ_K'] - 2 * df['KDJ_D']
        
        # 计算布林带
        upper, middle, lower = talib.BBANDS(close_values, 
                                           timeperiod=boll_params[0], nbdevup=boll_params[1], nbdevdn=boll_params[1])
        df['BOLL_UPPER'] = upper
        df['BOLL_MIDDLE'] = middle
        df['BOLL_LOWER'] = lower
        
        # 计算成交量均线（使用动态参数）
        for period_val in vma_periods:
            df[f'VMA{period_val}'] = talib.SMA(volume_values, timeperiod=period_val)
    elif USE_PANDAS_TA:
        # 使用pandas_ta计算技术指标
        # 计算移动平均线（使用动态参数）
        for period_val in ma_periods:
            df[f'MA{period_val}'] = ta.sma(df['收盘'], length=period_val)
        
        # 计算RSI
        df['RSI6'] = ta.rsi(df['收盘'], length=6)
        df['RSI12'] = ta.rsi(df['收盘'], length=12)
        df['RSI24'] = ta.rsi(df['收盘'], length=24)
        
        # 计算MACD
        macd_data = ta.macd(df['收盘'], fast=macd_params[0], slow=macd_params[1], signal=macd_params[2])
        df['MACD'] = macd_data[f'MACD_{macd_params[0]}_{macd_params[1]}_{macd_params[2]}']
        df['MACD_SIGNAL'] = macd_data[f'MACDs_{macd_params[0]}_{macd_params[1]}_{macd_params[2]}']
        df['MACD_HIST'] = macd_data[f'MACDh_{macd_params[0]}_{macd_params[1]}_{macd_params[2]}']
        
        # 计算KDJ
        stoch_data = ta.stoch(df['最高'], df['最低'], df['收盘'], k=kdj_params[0], d=kdj_params[1])
        df['KDJ_K'] = stoch_data[f'STOCHk_{kdj_params[0]}_{kdj_params[1]}_{kdj_params[2]}']
        df['KDJ_D'] = stoch_data[f'STOCHd_{kdj_params[0]}_{kdj_params[1]}_{kdj_params[2]}']
        df['KDJ_J'] = 3 * df['KDJ_K'] - 2 * df['KDJ_D']
        
        # 计算布林带
        bb_data = ta.bbands(df['收盘'], length=boll_params[0], std=boll_params[1])
        df['BOLL_UPPER'] = bb_data[f'BBU_{boll_params[0]}_{boll_params[1]}']
        df['BOLL_MIDDLE'] = bb_data[f'BBM_{boll_params[0]}_{boll_params[1]}']
        df['BOLL_LOWER'] = bb_data[f'BBL_{boll_params[0]}_{boll_params[1]}']
        
        # 计算成交量均线（使用动态参数）
        for period_val in vma_periods:
            df[f'VMA{period_val}'] = ta.sma(df['成交量'], length=period_val)
    else:
        # 使用pandas内置功能计算技术指标
        # 确保收盘价是float64类型
        close_prices = df['收盘'].astype('float64')
        high_prices = df['最高'].astype('float64')
        low_prices = df['最低'].astype('float64')
        volume = df['成交量'].astype('float64')
        
        # 计算移动平均线（使用动态参数）
        for period_val in ma_periods:
            df[f'MA{period_val}'] = close_prices.rolling(window=period_val).mean()
        
        # 计算RSI (简化版本)
        def calculate_rsi(prices, window):
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.astype('float64')
        
        df['RSI6'] = calculate_rsi(close_prices, 6)
        df['RSI12'] = calculate_rsi(close_prices, 12)
        df['RSI24'] = calculate_rsi(close_prices, 24)
        
        # 计算MACD (简化版本)
        ema12 = close_prices.ewm(span=macd_params[0]).mean()
        ema26 = close_prices.ewm(span=macd_params[1]).mean()
        df['MACD'] = (ema12 - ema26).astype('float64')
        df['MACD_SIGNAL'] = df['MACD'].ewm(span=macd_params[2]).mean().astype('float64')
        df['MACD_HIST'] = (df['MACD'] - df['MACD_SIGNAL']).astype('float64')
        
        # 计算KDJ (简化版本)
        def calculate_kdj(high, low, close, k_period, d_period):
            lowest_low = low.rolling(window=k_period).min()
            highest_high = high.rolling(window=k_period).max()
            rsv = (close - lowest_low) / (highest_high - lowest_low) * 100
            k = rsv.ewm(com=2).mean()
            d = k.ewm(com=2).mean()
            j = 3 * k - 2 * d
            return k.astype('float64'), d.astype('float64'), j.astype('float64')
        
        df['KDJ_K'], df['KDJ_D'], df['KDJ_J'] = calculate_kdj(high_prices, low_prices, close_prices, kdj_params[0], kdj_params[1])
        
        # 计算布林带 (简化版本)
        df['BOLL_MIDDLE'] = close_prices.rolling(window=boll_params[0]).mean().astype('float64')
        std = close_prices.rolling(window=boll_params[0]).std()
        df['BOLL_UPPER'] = (df['BOLL_MIDDLE'] + (std * boll_params[1])).astype('float64')
        df['BOLL_LOWER'] = (df['BOLL_MIDDLE'] - (std * boll_params[1])).astype('float64')
        
        # 计算成交量均线（使用动态参数）
        for period_val in vma_periods:
            df[f'VMA{period_val}'] = volume.rolling(window=period_val).mean().astype('float64')
    
    # 处理技术指标中的NaN值 - 对于技术指标，NaN通常表示数据不足，应该保持为NaN而不是0
    # 根据分钟周期构建技术指标列列表
    technical_columns = []
    for period_val in ma_periods:
        technical_columns.append(f'MA{period_val}')
    technical_columns.extend(['RSI6', 'RSI12', 'RSI24', 'MACD', 'MACD_SIGNAL', 'MACD_HIST', 
                             'KDJ_K', 'KDJ_D', 'KDJ_J', 'BOLL_UPPER', 'BOLL_MIDDLE', 'BOLL_LOWER'])
    for period_val in vma_periods:
        technical_columns.append(f'VMA{period_val}')
    
    for col in technical_columns:
        if col in df.columns:
            # 对于技术指标，保持NaN值，不填充为0
            # 这样可以更准确地表示数据不足的情况
            pass
    
    return df


def calculate_financial_health_scores(financial_row: pd.Series) -> dict:
    """
    计算财务健康度评分
    包括财务健康度评分、成长性评分、运营效率评分
    """
    scores = {}
    
    try:
        # 1. 财务健康度评分 (Financial Health Score)
        health_score = 0
        health_components = []
        
        # 盈利能力指标 (40%权重)
        roe = pd.to_numeric(financial_row['净资产收益率(%)'], errors='coerce')
        if pd.notna(roe):
            if roe >= 15:
                health_score += 40
                health_components.append(f"ROE优秀({roe:.2f}%)")
            elif roe >= 10:
                health_score += 30
                health_components.append(f"ROE良好({roe:.2f}%)")
            elif roe >= 5:
                health_score += 20
                health_components.append(f"ROE一般({roe:.2f}%)")
            else:
                health_score += 10
                health_components.append(f"ROE较差({roe:.2f}%)")
        
        # 偿债能力指标 (30%权重)
        current_ratio = pd.to_numeric(financial_row['流动比率'], errors='coerce')
        if pd.notna(current_ratio):
            if current_ratio >= 2.0:
                health_score += 30
                health_components.append(f"流动比率优秀({current_ratio:.2f})")
            elif current_ratio >= 1.5:
                health_score += 25
                health_components.append(f"流动比率良好({current_ratio:.2f})")
            elif current_ratio >= 1.0:
                health_score += 15
                health_components.append(f"流动比率一般({current_ratio:.2f})")
            else:
                health_score += 5
                health_components.append(f"流动比率较差({current_ratio:.2f})")
        
        # 运营效率指标 (30%权重)
        asset_turnover = pd.to_numeric(financial_row['总资产周转率(次)'], errors='coerce')
        if pd.notna(asset_turnover):
            if asset_turnover >= 1.0:
                health_score += 30
                health_components.append(f"资产周转优秀({asset_turnover:.2f})")
            elif asset_turnover >= 0.5:
                health_score += 25
                health_components.append(f"资产周转良好({asset_turnover:.2f})")
            elif asset_turnover >= 0.2:
                health_score += 15
                health_components.append(f"资产周转一般({asset_turnover:.2f})")
            else:
                health_score += 5
                health_components.append(f"资产周转较差({asset_turnover:.2f})")
        
        scores['财务健康度评分'] = min(health_score, 100)  # 确保不超过100分
        scores['财务健康度详情'] = "; ".join(health_components) if health_components else "数据不足"
        
        # 2. 成长性评分 (Growth Score)
        growth_score = 0
        growth_components = []
        
        # 收入增长率 (40%权重)
        revenue_growth = pd.to_numeric(financial_row['主营业务收入增长率(%)'], errors='coerce')
        if pd.notna(revenue_growth):
            if revenue_growth >= 20:
                growth_score += 40
                growth_components.append(f"收入增长优秀({revenue_growth:.2f}%)")
            elif revenue_growth >= 10:
                growth_score += 30
                growth_components.append(f"收入增长良好({revenue_growth:.2f}%)")
            elif revenue_growth >= 0:
                growth_score += 20
                growth_components.append(f"收入增长一般({revenue_growth:.2f}%)")
            else:
                growth_score += 5
                growth_components.append(f"收入增长负值({revenue_growth:.2f}%)")
        
        # 净利润增长率 (40%权重)
        profit_growth = pd.to_numeric(financial_row['净利润增长率(%)'], errors='coerce')
        if pd.notna(profit_growth):
            if profit_growth >= 20:
                growth_score += 40
                growth_components.append(f"利润增长优秀({profit_growth:.2f}%)")
            elif profit_growth >= 10:
                growth_score += 30
                growth_components.append(f"利润增长良好({profit_growth:.2f}%)")
            elif profit_growth >= 0:
                growth_score += 20
                growth_components.append(f"利润增长一般({profit_growth:.2f}%)")
            else:
                growth_score += 5
                growth_components.append(f"利润增长负值({profit_growth:.2f}%)")
        
        # 净资产增长率 (20%权重)
        equity_growth = pd.to_numeric(financial_row['净资产增长率(%)'], errors='coerce')
        if pd.notna(equity_growth):
            if equity_growth >= 15:
                growth_score += 20
                growth_components.append(f"净资产增长优秀({equity_growth:.2f}%)")
            elif equity_growth >= 5:
                growth_score += 15
                growth_components.append(f"净资产增长良好({equity_growth:.2f}%)")
            elif equity_growth >= 0:
                growth_score += 10
                growth_components.append(f"净资产增长一般({equity_growth:.2f}%)")
            else:
                growth_score += 2
                growth_components.append(f"净资产增长负值({equity_growth:.2f}%)")
        
        scores['成长性评分'] = min(growth_score, 100)
        scores['成长性详情'] = "; ".join(growth_components) if growth_components else "数据不足"
        
        # 3. 运营效率评分 (Operating Efficiency Score)
        efficiency_score = 0
        efficiency_components = []
        
        # 总资产周转率 (30%权重)
        if pd.notna(asset_turnover):
            if asset_turnover >= 1.0:
                efficiency_score += 30
                efficiency_components.append(f"总资产周转优秀({asset_turnover:.2f})")
            elif asset_turnover >= 0.5:
                efficiency_score += 25
                efficiency_components.append(f"总资产周转良好({asset_turnover:.2f})")
            elif asset_turnover >= 0.2:
                efficiency_score += 15
                efficiency_components.append(f"总资产周转一般({asset_turnover:.2f})")
            else:
                efficiency_score += 5
                efficiency_components.append(f"总资产周转较差({asset_turnover:.2f})")
        
        # 存货周转率 (25%权重)
        inventory_turnover = pd.to_numeric(financial_row['存货周转率(次)'], errors='coerce')
        if pd.notna(inventory_turnover):
            if inventory_turnover >= 6:
                efficiency_score += 25
                efficiency_components.append(f"存货周转优秀({inventory_turnover:.2f})")
            elif inventory_turnover >= 3:
                efficiency_score += 20
                efficiency_components.append(f"存货周转良好({inventory_turnover:.2f})")
            elif inventory_turnover >= 1:
                efficiency_score += 10
                efficiency_components.append(f"存货周转一般({inventory_turnover:.2f})")
            else:
                efficiency_score += 2
                efficiency_components.append(f"存货周转较差({inventory_turnover:.2f})")
        
        # 应收账款周转率 (25%权重)
        receivables_turnover = pd.to_numeric(financial_row['应收账款周转率(次)'], errors='coerce')
        if pd.notna(receivables_turnover):
            if receivables_turnover >= 12:
                efficiency_score += 25
                efficiency_components.append(f"应收周转优秀({receivables_turnover:.2f})")
            elif receivables_turnover >= 6:
                efficiency_score += 20
                efficiency_components.append(f"应收周转良好({receivables_turnover:.2f})")
            elif receivables_turnover >= 3:
                efficiency_score += 10
                efficiency_components.append(f"应收周转一般({receivables_turnover:.2f})")
            else:
                efficiency_score += 2
                efficiency_components.append(f"应收周转较差({receivables_turnover:.2f})")
        
        # 固定资产周转率 (20%权重)
        fixed_asset_turnover = pd.to_numeric(financial_row['固定资产周转率(次)'], errors='coerce')
        if pd.notna(fixed_asset_turnover):
            if fixed_asset_turnover >= 3:
                efficiency_score += 20
                efficiency_components.append(f"固定资产周转优秀({fixed_asset_turnover:.2f})")
            elif fixed_asset_turnover >= 1.5:
                efficiency_score += 15
                efficiency_components.append(f"固定资产周转良好({fixed_asset_turnover:.2f})")
            elif fixed_asset_turnover >= 0.5:
                efficiency_score += 10
                efficiency_components.append(f"固定资产周转一般({fixed_asset_turnover:.2f})")
            else:
                efficiency_score += 2
                efficiency_components.append(f"固定资产周转较差({fixed_asset_turnover:.2f})")
        
        scores['运营效率评分'] = min(efficiency_score, 100)
        scores['运营效率详情'] = "; ".join(efficiency_components) if efficiency_components else "数据不足"
        
        # 4. 综合评分
        total_score = (scores['财务健康度评分'] + scores['成长性评分'] + scores['运营效率评分']) / 3
        scores['综合财务评分'] = round(total_score, 1)
        
        # 5. 评分等级
        if total_score >= 80:
            scores['评分等级'] = "优秀"
        elif total_score >= 70:
            scores['评分等级'] = "良好"
        elif total_score >= 60:
            scores['评分等级'] = "一般"
        elif total_score >= 50:
            scores['评分等级'] = "较差"
        else:
            scores['评分等级'] = "需要关注"
        
    except Exception as e:
        scores['财务健康度评分'] = "N/A"
        scores['成长性评分'] = "N/A"
        scores['运营效率评分'] = "N/A"
        scores['综合财务评分'] = "N/A"
        scores['评分等级'] = "计算错误"
        scores['错误信息'] = str(e)
    
    return scores


def calculate_dynamic_valuation_indicators(symbol: str, retries: int = 5, timeout: float = 600) -> dict:
    """
    计算动态估值指标-指定股票代码
    基于stock_financial_analysis_indicator和stock_bid_ask_em接口
    """
    try:
        # 使用并行调用优化性能
        financial_data, current_price_data = parallel_financial_data_calls(symbol, retries, timeout)
        
        if financial_data is None or financial_data.empty:
            return {"error": "无法获取财务数据"}
        
        # 获取最新年度数据（优先12月31日）
        annual_data = financial_data[financial_data['日期'].str.contains('12-31', na=False)]
        if not annual_data.empty:
            latest_financial = annual_data.iloc[-1]
            data_type = "年度数据"
        else:
            latest_financial = financial_data.iloc[-1]
            data_type = "最新数据"
        
        if current_price_data is None or current_price_data.empty:
            return {"error": "无法获取当前股价"}
        
        # 从键值对格式中获取最新价
        latest_price_row = current_price_data[current_price_data['item'] == '最新']
        if latest_price_row.empty:
            return {"error": "无法获取最新价"}
        current_price = float(latest_price_row.iloc[0]['value'])
        
        # 3. 计算动态估值指标
        valuation_indicators = {}
        
        # 基础估值指标（处理极限情况）
        eps = pd.to_numeric(latest_financial['摊薄每股收益(元)'], errors='coerce')
        if pd.notna(eps) and eps > 0.01:  # 设置阈值，避免接近0的情况
            valuation_indicators['PE_动态'] = round(current_price / eps, 2)
        elif pd.notna(eps) and eps <= 0:  # 处理负收益或零收益情况
            valuation_indicators['PE_动态'] = "N/A (负收益或零收益)"
        else:
            valuation_indicators['PE_动态'] = "N/A"  # 数据缺失
        
        bps = pd.to_numeric(latest_financial['每股净资产_调整前(元)'], errors='coerce')
        if pd.notna(bps) and bps > 0.01:  # 设置阈值，避免接近0的情况
            valuation_indicators['PB_动态'] = round(current_price / bps, 2)
        elif pd.notna(bps) and bps <= 0:  # 处理负净资产情况
            valuation_indicators['PB_动态'] = "N/A (负净资产)"
        else:
            valuation_indicators['PB_动态'] = "N/A"  # 数据缺失
        
        cps = pd.to_numeric(latest_financial['每股经营性现金流(元)'], errors='coerce')
        if pd.notna(cps) and cps > 0.01:  # 设置阈值，避免接近0的情况
            valuation_indicators['PCF_动态'] = round(current_price / cps, 2)
        elif pd.notna(cps) and cps <= 0:  # 处理负现金流情况
            valuation_indicators['PCF_动态'] = "N/A (负现金流)"
        else:
            valuation_indicators['PCF_动态'] = "N/A"  # 数据缺失
        
        # 扩展估值指标（处理极限情况）
        w_eps = pd.to_numeric(latest_financial['加权每股收益(元)'], errors='coerce')
        if pd.notna(w_eps) and w_eps > 0.01:
            valuation_indicators['PE_加权'] = round(current_price / w_eps, 2)
        elif pd.notna(w_eps) and w_eps <= 0:
            valuation_indicators['PE_加权'] = "N/A (负收益或零收益)"
        else:
            valuation_indicators['PE_加权'] = "N/A"
        
        n_eps = pd.to_numeric(latest_financial['扣除非经常性损益后的每股收益(元)'], errors='coerce')
        if pd.notna(n_eps) and n_eps > 0.01:
            valuation_indicators['PE_扣非'] = round(current_price / n_eps, 2)
        elif pd.notna(n_eps) and n_eps <= 0:
            valuation_indicators['PE_扣非'] = "N/A (负收益或零收益)"
        else:
            valuation_indicators['PE_扣非'] = "N/A"
        
        adj_bps = pd.to_numeric(latest_financial['每股净资产_调整后(元)'], errors='coerce')
        if pd.notna(adj_bps) and adj_bps > 0.01:
            valuation_indicators['PB_调整后'] = round(current_price / adj_bps, 2)
        elif pd.notna(adj_bps) and adj_bps <= 0:
            valuation_indicators['PB_调整后'] = "N/A (负净资产)"
        else:
            valuation_indicators['PB_调整后'] = "N/A"
        
        # 每股价值指标（处理极限情况）
        cap_reserve = pd.to_numeric(latest_financial['每股资本公积金(元)'], errors='coerce')
        if pd.notna(cap_reserve) and cap_reserve > 0.01:
            valuation_indicators['每股资本公积金比率'] = round(current_price / cap_reserve, 2)
        elif pd.notna(cap_reserve) and cap_reserve <= 0:
            valuation_indicators['每股资本公积金比率'] = "N/A (负值或零值)"
        else:
            valuation_indicators['每股资本公积金比率'] = "N/A"
        
        undist_profit = pd.to_numeric(latest_financial['每股未分配利润(元)'], errors='coerce')
        if pd.notna(undist_profit) and undist_profit > 0.01:
            valuation_indicators['每股未分配利润比率'] = round(current_price / undist_profit, 2)
        elif pd.notna(undist_profit) and undist_profit <= 0:
            valuation_indicators['每股未分配利润比率'] = "N/A (负值或零值)"
        else:
            valuation_indicators['每股未分配利润比率'] = "N/A"
        
        # 成长性估值指标（处理极限情况）
        growth_rate = pd.to_numeric(latest_financial['净利润增长率(%)'], errors='coerce')
        if (pd.notna(growth_rate) and growth_rate > 0.01 and 
            'PE_动态' in valuation_indicators and 
            valuation_indicators['PE_动态'] != "N/A" and 
            isinstance(valuation_indicators['PE_动态'], (int, float)) and 
            valuation_indicators['PE_动态'] > 0):
            valuation_indicators['PEG'] = round(valuation_indicators['PE_动态'] / growth_rate, 2)
        else:
            valuation_indicators['PEG'] = "N/A"
        
        # 盈利能力估值指标（处理极限情况）
        roe = pd.to_numeric(latest_financial['净资产收益率(%)'], errors='coerce')
        if (pd.notna(roe) and 
            'PB_动态' in valuation_indicators and 
            valuation_indicators['PB_动态'] != "N/A" and 
            isinstance(valuation_indicators['PB_动态'], (int, float)) and 
            valuation_indicators['PB_动态'] > 0):
            valuation_indicators['市净率×ROE'] = round(valuation_indicators['PB_动态'] * roe, 2)
        else:
            valuation_indicators['市净率×ROE'] = "N/A"
        
        # 计算财务健康度评分
        health_scores = calculate_financial_health_scores(latest_financial)
        valuation_indicators.update(health_scores)
        
        # 添加元数据
        valuation_indicators['当前股价'] = current_price
        valuation_indicators['数据时间点'] = latest_financial['日期'].strftime('%Y-%m-%d') if hasattr(latest_financial['日期'], 'strftime') else str(latest_financial['日期'])
        valuation_indicators['数据类型'] = data_type
        
        return valuation_indicators
        
    except Exception as e:
        return {"error": f"计算动态估值指标失败: {str(e)}"}


def calculate_historical_valuation_indicators(df: pd.DataFrame, symbol: str, retries: int = 5, timeout: float = 600) -> pd.DataFrame:
    """
    计算历史估值指标-指定股票代码、周期(日频)、日期范围
    基于个股日频历史行情数据和财务数据，按日期排序计算历史估值指标
    统一使用早于计算日期的年报数据，按静态估值指标计算
    """
    try:
        # 使用缓存机制优化性能
        financial_cache = precompute_financial_cache(symbol, "2020")
        
        if not financial_cache:
            # 如果无法获取财务数据，返回原始数据
            print("警告：无法获取财务数据，返回原始历史数据")
            return df
        
        # 预处理数据
        result_df = preprocess_data_for_indicators(df)
        
        # 初始化所有历史估值指标列为object类型，避免dtype冲突
        result_df['PE_历史'] = "N/A"
        result_df['PB_历史'] = "N/A"
        result_df['PCF_历史'] = "N/A"
        result_df['PE_加权历史'] = "N/A"
        result_df['PE_扣非历史'] = "N/A"
        result_df['PB_调整后历史'] = "N/A"
        result_df['每股资本公积金比率_历史'] = "N/A"
        result_df['每股未分配利润比率_历史'] = "N/A"
        result_df['PEG_历史'] = "N/A"
        result_df['市净率×ROE_历史'] = "N/A"
        result_df['财务数据时间点'] = "N/A"
        
        print(f"找到 {len(financial_cache)} 个年报数据：{list(financial_cache.keys())}")
        
        # 遍历每个交易日，使用缓存的财务数据
        for index, row in result_df.iterrows():
            # 确保收盘价是数值类型
            current_price = pd.to_numeric(row['收盘'], errors='coerce')
            
            if pd.isna(current_price) or current_price <= 0:
                continue
            
            # 获取当前交易日的日期
            current_date = pd.to_datetime(row['日期'])
            current_year = current_date.year
            
            # 找到适用的年报数据（早于当前交易日的最新年报）
            applicable_years = [year for year in financial_cache.keys() if year < current_year]
            if not applicable_years:
                continue
            
            # 使用最新的年报数据
            latest_year = max(applicable_years)
            financial_data_row = financial_cache[latest_year]
            
            # 计算基础估值指标（处理极限情况）
            eps = financial_data_row['eps']
            if pd.notna(eps) and eps > 0.01:
                result_df.loc[index, 'PE_历史'] = str(round(current_price / eps, 2))
            else:
                result_df.loc[index, 'PE_历史'] = "N/A"
            
            bps = financial_data_row['bps']
            if pd.notna(bps) and bps > 0.01:
                result_df.loc[index, 'PB_历史'] = str(round(current_price / bps, 2))
            else:
                result_df.loc[index, 'PB_历史'] = "N/A"
            
            cps = financial_data_row['cps']
            if pd.notna(cps) and cps > 0.01:
                result_df.loc[index, 'PCF_历史'] = str(round(current_price / cps, 2))
            else:
                result_df.loc[index, 'PCF_历史'] = "N/A"
            
            # 计算扩展估值指标（处理极限情况）
            w_eps = financial_data_row['w_eps']
            if pd.notna(w_eps) and w_eps > 0.01:
                result_df.loc[index, 'PE_加权历史'] = str(round(current_price / w_eps, 2))
            else:
                result_df.loc[index, 'PE_加权历史'] = "N/A"
            
            n_eps = financial_data_row['n_eps']
            if pd.notna(n_eps) and n_eps > 0.01:
                result_df.loc[index, 'PE_扣非历史'] = str(round(current_price / n_eps, 2))
            else:
                result_df.loc[index, 'PE_扣非历史'] = "N/A"
            
            adj_bps = financial_data_row['adj_bps']
            if pd.notna(adj_bps) and adj_bps > 0.01:
                result_df.loc[index, 'PB_调整后历史'] = str(round(current_price / adj_bps, 2))
            else:
                result_df.loc[index, 'PB_调整后历史'] = "N/A"
            
            # 计算每股价值指标（处理极限情况）
            cap_reserve = financial_data_row['cap_reserve']
            if pd.notna(cap_reserve) and cap_reserve > 0.01:
                result_df.loc[index, '每股资本公积金比率_历史'] = str(round(current_price / cap_reserve, 2))
            else:
                result_df.loc[index, '每股资本公积金比率_历史'] = "N/A"
            
            undist_profit = financial_data_row['undist_profit']
            if pd.notna(undist_profit) and undist_profit > 0.01:
                result_df.loc[index, '每股未分配利润比率_历史'] = str(round(current_price / undist_profit, 2))
            else:
                result_df.loc[index, '每股未分配利润比率_历史'] = "N/A"
            
            # 计算成长性估值指标（处理极限情况）
            growth_rate = financial_data_row['growth_rate']
            if (pd.notna(growth_rate) and growth_rate > 0.01 and 
                result_df.loc[index, 'PE_历史'] != "N/A" and 
                isinstance(result_df.loc[index, 'PE_历史'], str) and result_df.loc[index, 'PE_历史'].replace('.', '').isdigit()):
                pe_value = float(result_df.loc[index, 'PE_历史'])
                if pe_value > 0:
                    result_df.loc[index, 'PEG_历史'] = str(round(pe_value / growth_rate, 2))
                else:
                    result_df.loc[index, 'PEG_历史'] = "N/A"
            else:
                result_df.loc[index, 'PEG_历史'] = "N/A"
            
            # 计算盈利能力估值指标（处理极限情况）
            roe = financial_data_row['roe']
            if (pd.notna(roe) and 
                result_df.loc[index, 'PB_历史'] != "N/A" and 
                isinstance(result_df.loc[index, 'PB_历史'], str) and result_df.loc[index, 'PB_历史'].replace('.', '').isdigit()):
                pb_value = float(result_df.loc[index, 'PB_历史'])
                if pb_value > 0:
                    result_df.loc[index, '市净率×ROE_历史'] = str(round(pb_value * roe, 2))
                else:
                    result_df.loc[index, '市净率×ROE_历史'] = "N/A"
            else:
                result_df.loc[index, '市净率×ROE_历史'] = "N/A"
            
            # 添加财务数据时间点信息（转换为字符串以避免JSON序列化问题）
            result_df.loc[index, '财务数据时间点'] = financial_data_row['date'].strftime('%Y-%m-%d')
        
        return result_df
        
    except Exception as e:
        # 如果计算失败，返回原始数据
        print(f"计算历史估值指标失败: {str(e)}")
        return df


def calculate_stock_basic_info_summary(symbol: str, retries: int = 5, timeout: float = 600) -> dict:
    """
    计算个股基本信息汇总-指定股票代码
    整合多个接口，提供个股的全面基本信息
    """
    try:
        summary = {
            # 1. 证券资料 (ak.stock_individual_info_em)
            "证券资料": {
                "股票代码": "",
                "股票简称": "",
                "所属行业": "",
                "最新价格": "",
                "总市值": "",
                "流通市值": "",
                "总股本": "",
                "流通股": ""
            },
            
            # 2. 公司概况 (ak.stock_profile_cninfo)
            "公司概况": {
                "公司全称": "",
                "所属市场": "",
                "成立时间": "",
                "上市时间": "",
                "法人代表": "",
                "注册地址": "",
                "办公地址": "",
                "官方网站": "",
                "联系方式": ""
            },
            
            # 3. 主营业务 (ak.stock_zyjs_ths)
            "主营业务": {
                "主营业务": "",
                "经营范围": "",
                "产品类型": "",
                "产品名称": ""
            },
            
            # 4. 主营业务构成 (ak.stock_zygc_em)
            "主营业务构成": {
                "业务构成详情": ""
            },
            
            # 5. 元数据
            "元数据": {
                "数据更新时间": "",
                "数据来源": "AKShare",
                "接口状态": {}
            }
        }
        
        # 使用并行调用优化性能
        api_results = parallel_basic_info_calls(symbol, retries, timeout)
        
        # 1. 处理证券资料 (ak.stock_individual_info_em)
        basic_info = api_results.get('basic_info')
        if basic_info is not None and not basic_info.empty:
            # 转换为字典格式便于查找
            basic_dict = dict(zip(basic_info['item'], basic_info['value']))
            summary["证券资料"]["股票代码"] = str(basic_dict.get('股票代码', ''))
            summary["证券资料"]["股票简称"] = str(basic_dict.get('股票简称', ''))
            summary["证券资料"]["所属行业"] = str(basic_dict.get('行业', ''))
            summary["证券资料"]["最新价格"] = str(basic_dict.get('最新', ''))
            summary["证券资料"]["总市值"] = str(basic_dict.get('总市值', ''))
            summary["证券资料"]["流通市值"] = str(basic_dict.get('流通市值', ''))
            summary["证券资料"]["总股本"] = str(basic_dict.get('总股本', ''))
            summary["证券资料"]["流通股"] = str(basic_dict.get('流通股', ''))
            summary["元数据"]["接口状态"]["stock_individual_info_em"] = "成功"
        else:
            summary["元数据"]["接口状态"]["stock_individual_info_em"] = "失败"
        
        # 2. 处理公司概况 (ak.stock_profile_cninfo)
        company_info = api_results.get('company_info')
        if company_info is not None and not company_info.empty:
                company_row = company_info.iloc[0]
                
                summary["公司概况"]["公司全称"] = str(company_row.get('公司名称', ''))
                summary["公司概况"]["所属市场"] = str(company_row.get('所属市场', ''))
                summary["公司概况"]["成立时间"] = str(company_row.get('成立日期', ''))
                summary["公司概况"]["上市时间"] = str(company_row.get('上市日期', ''))
                summary["公司概况"]["法人代表"] = str(company_row.get('法人代表', ''))
                summary["公司概况"]["注册地址"] = str(company_row.get('注册地址', ''))
                summary["公司概况"]["办公地址"] = str(company_row.get('办公地址', ''))
                summary["公司概况"]["官方网站"] = str(company_row.get('官方网站', ''))
                
                # 组合联系方式
                phone = str(company_row.get('联系电话', ''))
                email = str(company_row.get('电子邮箱', ''))
                contact_info = []
                if phone and phone != 'nan':
                    contact_info.append(f"电话: {phone}")
                if email and email != 'nan':
                    contact_info.append(f"邮箱: {email}")
                summary["公司概况"]["联系方式"] = "；".join(contact_info) if contact_info else ""
                
                summary["元数据"]["接口状态"]["stock_profile_cninfo"] = "成功"
        else:
            summary["元数据"]["接口状态"]["stock_profile_cninfo"] = "失败"
        
        # 3. 处理主营业务 (ak.stock_zyjs_ths)
        business_info = api_results.get('business_info')
        if business_info is not None and not business_info.empty:
            business_row = business_info.iloc[0]
            
            summary["主营业务"]["主营业务"] = str(business_row.get('主营业务', ''))
            summary["主营业务"]["经营范围"] = str(business_row.get('经营范围', ''))
            summary["主营业务"]["产品类型"] = str(business_row.get('产品类型', ''))
            summary["主营业务"]["产品名称"] = str(business_row.get('产品名称', ''))
            
            summary["元数据"]["接口状态"]["stock_zyjs_ths"] = "成功"
        else:
            summary["元数据"]["接口状态"]["stock_zyjs_ths"] = "失败"
        
        # 4. 处理主营业务构成 (ak.stock_zygc_em)
        try:
            # 为股票代码添加市场标识
            if len(symbol) == 6 and symbol.isdigit():
                if symbol.startswith(('60', '68', '90')):
                    market_symbol = f"SH{symbol}"  # 上交所
                elif symbol.startswith(('00', '30')):
                    market_symbol = f"SZ{symbol}"  # 深交所
                else:
                    market_symbol = f"SH{symbol}"  # 默认上交所
            else:
                market_symbol = symbol  # 如果已经包含市场标识，直接使用
            
            business_structure = safe_ak_call(
                ak.stock_zygc_em,
                retries=2,  # 现在接口稳定了，可以增加重试次数
                timeout=timeout,
                symbol=market_symbol
            )
            if business_structure is not None and not business_structure.empty:
                structure_info = extract_business_structure(business_structure)
                summary["主营业务构成"]["业务构成详情"] = structure_info
                summary["元数据"]["接口状态"]["stock_zygc_em"] = "成功"
            else:
                summary["主营业务构成"]["业务构成详情"] = "N/A (接口无数据)"
                summary["元数据"]["接口状态"]["stock_zygc_em"] = "失败"
        except Exception as e:
            # 特殊处理'zygcfx'错误和其他错误
            if "'zygcfx'" in str(e):
                summary["主营业务构成"]["业务构成详情"] = "N/A (接口数据结构变更)"
                summary["元数据"]["接口状态"]["stock_zygc_em"] = "接口数据结构变更"
            else:
                summary["主营业务构成"]["业务构成详情"] = "N/A"
                summary["元数据"]["接口状态"]["stock_zygc_em"] = f"错误: {str(e)}"
        
        # 设置数据更新时间
        from datetime import datetime
        summary["元数据"]["数据更新时间"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return summary
        
    except Exception as e:
        return {"error": f"计算个股基本信息汇总失败: {str(e)}"}


def extract_business_structure(business_structure_df):
    """提取业务构成信息"""
    if business_structure_df is None or business_structure_df.empty:
        return "N/A"
    
    try:
        # 检查是否有必要的列
        if '分类类型' not in business_structure_df.columns:
            # 如果没有分类类型列，直接返回前几行数据
            structure_info = []
            for idx, row in business_structure_df.head(3).iterrows():
                if '主营构成' in row and pd.notna(row['主营构成']):
                    product_name = str(row['主营构成'])
                    if product_name and product_name != 'nan':
                        income_ratio = row.get('收入比例', 0)
                        # 安全地转换收入比例为数值
                        try:
                            income_ratio_val = float(income_ratio) if pd.notna(income_ratio) else 0
                            if income_ratio_val > 0:
                                structure_info.append(f"{product_name} (收入占比{income_ratio_val:.1%})")
                            else:
                                structure_info.append(product_name)
                        except (ValueError, TypeError):
                            structure_info.append(product_name)
            return "；".join(structure_info) if structure_info else "N/A"
        
        # 按分类类型分别处理
        structure_info = []
        
        # 处理按产品分类
        if '按产品分类' in business_structure_df['分类类型'].values:
            product_data = business_structure_df[business_structure_df['分类类型'] == '按产品分类']
            if not product_data.empty:
                for idx, row in product_data.head(2).iterrows():  # 取前2个产品
                    product_name = str(row.get('主营构成', ''))
                    income_ratio = row.get('收入比例', 0)
                    if product_name and product_name != 'nan':
                        # 安全地转换收入比例为数值
                        try:
                            income_ratio_val = float(income_ratio) if pd.notna(income_ratio) else 0
                            if income_ratio_val > 0:
                                structure_info.append(f"产品：{product_name} (收入占比{income_ratio_val:.1%})")
                            else:
                                structure_info.append(f"产品：{product_name}")
                        except (ValueError, TypeError):
                            structure_info.append(f"产品：{product_name}")
        
        # 处理按地区分类
        if '按地区分类' in business_structure_df['分类类型'].values:
            region_data = business_structure_df[business_structure_df['分类类型'] == '按地区分类']
            if not region_data.empty:
                for idx, row in region_data.head(2).iterrows():  # 取前2个地区
                    region_name = str(row.get('主营构成', ''))
                    income_ratio = row.get('收入比例', 0)
                    if region_name and region_name != 'nan':
                        # 安全地转换收入比例为数值
                        try:
                            income_ratio_val = float(income_ratio) if pd.notna(income_ratio) else 0
                            if income_ratio_val > 0:
                                structure_info.append(f"地区：{region_name} (收入占比{income_ratio_val:.1%})")
                            else:
                                structure_info.append(f"地区：{region_name}")
                        except (ValueError, TypeError):
                            structure_info.append(f"地区：{region_name}")
        
        return "；".join(structure_info) if structure_info else "N/A"
        
    except Exception as e:
        return f"数据解析错误: {str(e)}"


def format_basic_info_as_table(summary_data):
    """将基本信息格式化为Markdown表格"""
    text_output = "# 个股基本信息汇总\n\n"
    
    # 股票身份表格
    text_output += "## 股票身份\n"
    text_output += "| 项目 | 值 |\n"
    text_output += "|------|-----|\n"
    text_output += f"| 股票代码 | {summary_data['股票身份']['股票代码']} |\n"
    text_output += f"| 股票简称 | {summary_data['股票身份']['股票简称']} |\n"
    text_output += f"| 公司全称 | {summary_data['股票身份']['公司全称']} |\n"
    text_output += f"| 所属市场 | {summary_data['股票身份']['所属市场']} |\n"
    text_output += f"| 所属行业 | {summary_data['股票身份']['所属行业']} |\n\n"
    
    # 当前状态表格
    text_output += "## 当前状态\n"
    text_output += "| 项目 | 值 |\n"
    text_output += "|------|-----|\n"
    text_output += f"| 最新价格 | {summary_data['当前状态']['最新价格']} |\n"
    text_output += f"| 总市值 | {summary_data['当前状态']['总市值']} |\n"
    text_output += f"| 流通市值 | {summary_data['当前状态']['流通市值']} |\n"
    text_output += f"| 总股本 | {summary_data['当前状态']['总股本']} |\n"
    text_output += f"| 流通股 | {summary_data['当前状态']['流通股']} |\n\n"
    
    # 公司概况表格
    text_output += "## 公司概况\n"
    text_output += "| 项目 | 值 |\n"
    text_output += "|------|-----|\n"
    text_output += f"| 成立时间 | {summary_data['公司概况']['成立时间']} |\n"
    text_output += f"| 上市时间 | {summary_data['公司概况']['上市时间']} |\n"
    text_output += f"| 法人代表 | {summary_data['公司概况']['法人代表']} |\n"
    text_output += f"| 注册地址 | {summary_data['公司概况']['注册地址']} |\n"
    text_output += f"| 办公地址 | {summary_data['公司概况']['办公地址']} |\n"
    text_output += f"| 官方网站 | {summary_data['公司概况']['官方网站']} |\n"
    text_output += f"| 联系方式 | {summary_data['公司概况']['联系方式']} |\n\n"
    
    # 业务描述表格
    text_output += "## 业务描述\n"
    text_output += "| 项目 | 值 |\n"
    text_output += "|------|-----|\n"
    text_output += f"| 主营业务 | {summary_data['业务描述']['主营业务']} |\n"
    text_output += f"| 产品服务 | {summary_data['业务描述']['产品服务']} |\n"
    text_output += f"| 经营范围 | {summary_data['业务描述']['经营范围']} |\n"
    text_output += f"| 业务构成 | {summary_data['业务描述']['业务构成']} |\n"
    
    return text_output


def get_indicator_columns(indicator_type: str, period: str = "daily") -> list:
    """
    根据指标类型和周期返回对应的输出列
    """
    if indicator_type == "trend_momentum_oscillator":
        # 基础列（所有周期都包含）
        base_columns = [
            # 原始行情数据
            '日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率',
            # RSI相对强弱指标
            'RSI6', 'RSI12', 'RSI24',
            # MACD指标
            'MACD', 'MACD_SIGNAL', 'MACD_HIST',
            # KDJ随机指标
            'KDJ_K', 'KDJ_D', 'KDJ_J',
            # 布林带指标
            'BOLL_UPPER', 'BOLL_MIDDLE', 'BOLL_LOWER'
        ]
        
        # 使用统一的股票分析领域标准技术指标列
        # 无论什么时间周期，技术指标列都保持一致
        base_columns.extend(['MA5', 'MA10', 'MA20', 'MA30', 'MA60'])
        base_columns.extend(['VMA5', 'VMA10', 'VMA20'])
        
        return base_columns
    elif indicator_type == "trend_momentum_oscillator_minute":
        # 分钟级指标基础列
        base_columns = [
            # 原始行情数据（分钟级数据可能包含时间列）
            '时间', '开盘', '收盘', '最高', '最低', '成交量', '成交额',
            # RSI相对强弱指标
            'RSI6', 'RSI12', 'RSI24',
            # MACD指标
            'MACD', 'MACD_SIGNAL', 'MACD_HIST',
            # KDJ随机指标
            'KDJ_K', 'KDJ_D', 'KDJ_J',
            # 布林带指标
            'BOLL_UPPER', 'BOLL_MIDDLE', 'BOLL_LOWER'
        ]
        
        # 根据分钟级数据的实际列添加可选列
        optional_columns = ['均价', '振幅', '涨跌幅', '涨跌额', '换手率']
        base_columns.extend(optional_columns)
        
        # 使用统一的股票分析领域标准技术指标列
        # 无论什么时间周期，技术指标列都保持一致
        base_columns.extend(['MA5', 'MA10', 'MA20', 'MA30', 'MA60'])
        base_columns.extend(['VMA5', 'VMA10', 'VMA20'])
        
        return base_columns
    elif indicator_type == "dynamic_valuation_indicators":
        return [
            # 动态估值指标
            'PE_动态', 'PB_动态', 'PCF_动态', 'PE_加权', 'PE_扣非', 'PB_调整后',
            '每股资本公积金比率', '每股未分配利润比率', 'PEG', '市净率×ROE', '市销率×净利率',
            # 财务健康度评分
            '财务健康度评分', '财务健康度详情', '成长性评分', '成长性详情', 
            '运营效率评分', '运营效率详情', '综合财务评分', '评分等级',
            # 元数据
            '当前股价', '数据时间点', '数据类型'
        ]
    elif indicator_type == "historical_valuation_indicators":
        return [
            # 原始行情数据
            '日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率',
            # 历史估值指标
            'PE_历史', 'PB_历史', 'PCF_历史', 'PE_加权历史', 'PE_扣非历史', 'PB_调整后历史',
            '每股资本公积金比率_历史', '每股未分配利润比率_历史', 'PEG_历史', '市净率×ROE_历史',
            # 元数据
            '财务数据时间点'
        ]
    elif indicator_type == "stock_basic_info_summary":
        return [
            # 证券资料 (ak.stock_individual_info_em)
            '股票代码', '股票简称', '所属行业', '最新价格', '总市值', '流通市值', '总股本', '流通股',
            # 公司概况 (ak.stock_profile_cninfo)
            '公司全称', '所属市场', '成立时间', '上市时间', '法人代表', '注册地址', '办公地址', '官方网站', '联系方式',
            # 主营业务 (ak.stock_zyjs_ths)
            '主营业务', '经营范围', '产品类型', '产品名称',
            # 主营业务构成 (ak.stock_zygc_em)
            '业务构成详情',
            # 元数据
            '数据更新时间', '数据来源', '接口状态'
        ]
    else:
        return ['日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']  # 默认返回原始数据


class StockComprehensiveTechnicalIndicatorsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        # 初始化错误处理组件（延迟初始化）
        if not hasattr(self, 'error_logger'):
            self.error_logger = ErrorLogger("stock_comprehensive_indicators")
            self.error_formatter = ErrorMessageFormatter()
            self.retry_manager = RetryStrategyManager()
            self.recovery_handler = ErrorRecoveryHandler()
            self.report_generator = ErrorReportGenerator()
        
        # 创建错误上下文
        context = ErrorContext(
            operation="stock_comprehensive_technical_indicators",
            symbol=tool_parameters.get("symbol", ""),
            user_id=tool_parameters.get("user_id", "unknown")
        )
        
        try:
            self.error_logger.log_info("Tool invocation started", context)
            context.add_step("参数解析", success=True)
            
            # 参数解析和验证
            params = self._parse_and_validate_parameters(tool_parameters, context)
            if not params:
                return
            
            context.add_step("参数验证", success=True)
            
            # 根据指标类型选择处理方式
            if params['indicator'] == "stock_basic_info_summary":
                yield from self._handle_basic_info_summary(params, context)
            elif params['indicator'] == "dynamic_valuation_indicators":
                yield from self._handle_dynamic_valuation(params, context)
            else:
                yield from self._handle_historical_indicators(params, context)
                
        except StockDataError as e:
            context.add_error(e)
            self.error_logger.log_error(e, context)
            yield from self._handle_stock_data_error(e, context)
        except Exception as e:
            # 将通用异常转换为StockDataError
            stock_error = StockDataError(
                message=f"未预期的错误: {str(e)}",
                error_code="UNEXPECTED_ERROR",
                details={'original_error': str(e), 'error_type': type(e).__name__}
            )
            context.add_error(stock_error)
            self.error_logger.log_error(stock_error, context)
            yield from self._handle_stock_data_error(stock_error, context)
    
    def _parse_and_validate_parameters(self, tool_parameters: dict[str, Any], context: ErrorContext) -> Optional[Dict[str, Any]]:
        """解析和验证参数"""
        try:
            symbol = tool_parameters.get("symbol", "")
            start_date = tool_parameters.get("start_date", "20250101")
            end_date = tool_parameters.get("end_date", "")
            period_daily = tool_parameters.get("period_daily", "daily")
            period_minute = tool_parameters.get("period_minute", "5")
            adjust = tool_parameters.get("adjust", "qfq")
            indicator = tool_parameters.get("indicator", "trend_momentum_oscillator")
            
            # 处理复权方式参数
            if adjust == "none":
                adjust = ""
            
            # 处理结束日期缺省值（当前日期）
            if not end_date:
                from datetime import datetime
                end_date = datetime.now().strftime("%Y%m%d")
            
            retries = int(tool_parameters.get("retries", 5))
            timeout = float(tool_parameters.get("timeout", 600))
            
            # 参数验证
            if not symbol:
                raise DataValidationError(
                    message="股票代码不能为空",
                    validation_type="required_field",
                    details={'field': 'symbol', 'value': symbol}
                )
            
            # 根据指标类型确定使用的周期参数
            if indicator == "trend_momentum_oscillator_minute":
                period = period_minute
            elif indicator in ["trend_momentum_oscillator", "historical_valuation_indicators"]:
                period = period_daily
            else:
                period = None  # 动态估值指标和基本信息汇总不需要周期参数
                
            # 动态估值指标不需要日期参数
            if indicator not in ["dynamic_valuation_indicators", "stock_basic_info_summary"]:
                # 对于分钟级指标，需要处理日期时间格式
                if indicator == "trend_momentum_oscillator_minute":
                    # 分钟级指标需要日期时间格式
                    try:
                        # 将日期转换为日期时间格式
                        if len(start_date) == 8:  # YYYYMMDD格式
                            start_date = f"{start_date[:4]}-{start_date[4:6]}-{start_date[6:8]} 09:30:00"
                        elif len(start_date) == 10:  # YYYY-MM-DD格式
                            start_date = f"{start_date} 09:30:00"
                        # 如果已经是完整格式，保持不变
                        
                        if len(end_date) == 8:  # YYYYMMDD格式
                            end_date = f"{end_date[:4]}-{end_date[4:6]}-{end_date[6:8]} 15:00:00"
                        elif len(end_date) == 10:  # YYYY-MM-DD格式
                            end_date = f"{end_date} 15:00:00"
                        # 如果已经是完整格式，保持不变
                        
                        # 验证日期时间格式
                        pd.to_datetime(start_date)
                        pd.to_datetime(end_date)
                    except Exception as date_error:
                        raise DataValidationError(
                            message="日期格式错误，请使用YYYYMMDD或YYYY-MM-DD格式",
                            validation_type="invalid_format",
                            details={'fields': ['start_date', 'end_date'], 'error': str(date_error)}
                        )
                else:
                    # 其他指标使用日期格式
                    try:
                        pd.to_datetime(start_date)
                        pd.to_datetime(end_date)
                    except Exception as date_error:
                        raise DataValidationError(
                            message="日期格式错误，请使用YYYYMMDD格式",
                            validation_type="invalid_format",
                            details={'fields': ['start_date', 'end_date'], 'error': str(date_error)}
                        )
            
            return {
                'symbol': symbol,
                'start_date': start_date,
                'end_date': end_date,
                'period': period,
                'period_daily': period_daily,
                'period_minute': period_minute,
                'adjust': adjust,
                'indicator': indicator,
                'retries': retries,
                'timeout': timeout
            }
            
        except DataValidationError:
            raise
        except Exception as e:
            raise DataValidationError(
                message=f"参数解析失败: {str(e)}",
                validation_type="parsing_error",
                details={'error': str(e)}
            )
    
    def _handle_stock_data_error(self, error: StockDataError, context: ErrorContext) -> Generator[ToolInvokeMessage]:
        """处理股票数据错误"""
        try:
            # 尝试错误恢复
            recovery_result = self.recovery_handler.attempt_recovery(error, context)
            if recovery_result:
                context.add_step("错误恢复", success=True)
                yield self.create_text_message("错误已自动恢复，继续处理...")
            return
        
            # 生成错误报告
            error_report = self.report_generator.generate_user_report(error, context)
            
            # 输出用户友好的错误信息
            user_message = f"{self.error_formatter.format_error(error)}\n\n{self.error_formatter.format_suggestion(error)}"
            yield self.create_text_message(user_message)
            
            # 输出技术详情（用于调试）
            technical_details = self.error_formatter.format_technical_details(error)
            yield self.create_text_message(f"技术详情:\n{technical_details}")
            
            # 输出JSON格式的错误信息
            yield self.create_json_message({
                "error": error.to_dict(),
                "context": context.get_summary(),
                "recovery_attempted": recovery_result is not None
            })
            
        except Exception as e:
            # 如果错误处理本身出错，输出简单错误信息
            yield self.create_text_message(f"错误处理失败: {str(e)}")
            yield self.create_json_message({"error": f"error handling failed: {str(e)}"})
    
    def _handle_basic_info_summary(self, params: Dict[str, Any], context: ErrorContext) -> Generator[ToolInvokeMessage]:
        """处理基本信息汇总"""
        try:
            context.add_step("基本信息汇总计算", success=True)
            
            summary_result = calculate_stock_basic_info_summary(
                params['symbol'], 
                params['retries'], 
                params['timeout']
            )
            
            if "error" in summary_result:
                raise DataFetchError(
                    message=f"个股基本信息汇总计算失败: {summary_result['error']}",
                    api_name="basic_info_summary",
                    symbol=params['symbol']
                )
            
            # 格式化为Markdown表格
            text_output = self._format_basic_info_as_table(summary_result)
            yield self.create_text_message(text_output)
            
            # 输出JSON数据
            yield self.create_json_message({"data": summary_result})
            context.add_step("基本信息汇总输出", success=True)
                
        except StockDataError:
            raise
        except Exception as e:
            raise CalculationError(
                message=f"基本信息汇总计算错误: {str(e)}",
                indicator_type="basic_info_summary",
                details={'symbol': params['symbol'], 'error': str(e)}
            )
    
    def _format_basic_info_as_table(self, summary_result: dict) -> str:
        """将基本信息格式化为Markdown表格"""
        try:
            text_output = ""
            
            # 证券资料 (ak.stock_individual_info_em)
            if "证券资料" in summary_result:
                text_output += "### 证券资料\n"
                text_output += "| 项目 | 信息 |\n"
                text_output += "|------|------|\n"
                for key, value in summary_result["证券资料"].items():
                    if value:  # 只显示非空值
                        text_output += f"| {key} | {value} |\n"
                text_output += "\n"
            
            # 公司概况 (ak.stock_profile_cninfo)
            if "公司概况" in summary_result:
                text_output += "### 公司概况\n"
                text_output += "| 项目 | 信息 |\n"
                text_output += "|------|------|\n"
                for key, value in summary_result["公司概况"].items():
                    if value:  # 只显示非空值
                        text_output += f"| {key} | {value} |\n"
                text_output += "\n"
            
            # 主营业务 (ak.stock_zyjs_ths)
            if "主营业务" in summary_result:
                text_output += "### 主营业务\n"
                text_output += "| 项目 | 信息 |\n"
                text_output += "|------|------|\n"
                for key, value in summary_result["主营业务"].items():
                    if value:  # 只显示非空值
                        text_output += f"| {key} | {value} |\n"
                text_output += "\n"
            
            # 主营业务构成 (ak.stock_zygc_em)
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
    
    def _handle_dynamic_valuation(self, params: Dict[str, Any], context: ErrorContext) -> Generator[ToolInvokeMessage]:
        """处理动态估值指标"""
        try:
            context.add_step("动态估值指标计算", success=True)
            
            valuation_result = calculate_dynamic_valuation_indicators(
                params['symbol'], 
                params['retries'], 
                params['timeout']
            )
            
            if "error" in valuation_result:
                raise DataFetchError(
                    message=f"动态估值指标计算失败: {valuation_result['error']}",
                    api_name="dynamic_valuation",
                    symbol=params['symbol']
                )
            
            # 将估值指标转换为DataFrame格式
            valuation_df = pd.DataFrame([valuation_result])
            
            # 输出结果 - 使用兼容的Markdown格式
            yield from self._output_compatible_markdown(valuation_df)
            context.add_step("动态估值指标输出", success=True)
                
        except StockDataError:
            raise
        except Exception as e:
            raise CalculationError(
                message=f"动态估值指标计算错误: {str(e)}",
                indicator_type="dynamic_valuation",
                details={'symbol': params['symbol'], 'error': str(e)}
            )
    
    def _handle_historical_indicators(self, params: Dict[str, Any], context: ErrorContext) -> Generator[ToolInvokeMessage]:
        """处理历史指标计算"""
        try:
            context.add_step("历史数据获取", success=True)
            
            # 根据指标类型选择数据源
            if params['indicator'] == "trend_momentum_oscillator_minute":
                # 分钟级数据获取
                result = safe_ak_call(
                    ak.stock_zh_a_hist_min_em,
                    retries=params['retries'],
                    timeout=params['timeout'],
                    symbol=params['symbol'],
                    start_date=params['start_date'],
                    end_date=params['end_date'],
                    period=params['period'],
                    adjust=params['adjust']
                )
            else:
                # 日/周/月级数据获取
                result = safe_ak_call(
                    ak.stock_zh_a_hist,
                    retries=params['retries'],
                    timeout=params['timeout'],
                    symbol=params['symbol'],
                    period=params['period'],
                    start_date=params['start_date'],
                    end_date=params['end_date'],
                    adjust=params['adjust']
                )
            
            # 统一的数据验证
            if result is None or result.empty or len(result.columns) == 0:
                raise DataFetchError(
                    message="暂无历史数据，可能是无效的股票代码",
                    api_name="stock_zh_a_hist" if params['indicator'] != "trend_momentum_oscillator_minute" else "stock_zh_a_hist_min_em",
                    symbol=params['symbol'],
                    details={'start_date': params['start_date'], 'end_date': params['end_date']}
                )
            
            context.add_step("历史数据处理", success=True)
            
            # 使用预处理函数优化数据处理
            df = preprocess_data_for_indicators(result)
                
                # 根据指标类型选择计算函数
            if params['indicator'] == "trend_momentum_oscillator":
                df = calculate_trend_momentum_oscillator(df, params['period'])
            elif params['indicator'] == "trend_momentum_oscillator_minute":
                df = calculate_trend_momentum_oscillator_minute(df, params['period'])
            elif params['indicator'] == "historical_valuation_indicators":
                df = calculate_historical_valuation_indicators(df, params['symbol'], params['retries'], params['timeout'])
            
            context.add_step("指标计算", success=True)
                
                # 根据指标类型选择输出列
            if params['indicator'] == "trend_momentum_oscillator_minute":
                output_columns = get_indicator_columns(params['indicator'], params['period_minute'])
            else:
                output_columns = get_indicator_columns(params['indicator'], params['period'])
            # 只选择实际存在的列
            available_columns = [col for col in output_columns if col in df.columns]
            result_df = df[available_columns].copy()
            
            # 优化内存使用
            result_df = optimize_dataframe_memory(result_df)
            
            # 确保日期/时间列是字符串格式以避免JSON序列化问题
            if '日期' in result_df.columns:
                result_df['日期'] = result_df['日期'].dt.strftime('%Y-%m-%d')
            elif '时间' in result_df.columns:
                # 处理分钟级数据的时间列
                result_df['时间'] = pd.to_datetime(result_df['时间']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # 确保所有列都是JSON序列化兼容的
            result_df = ensure_json_serializable(result_df)
                
            # 对分钟级指标进行合理限制（按股票分析惯例）
            if params['indicator'] == "trend_momentum_oscillator_minute":
                # 分钟级数据按股票分析惯例，通常分析最近5-10个交易日
                # 根据周期调整保留的交易日数
                if params['period'] == "1":  # 1分钟
                    default_max_days = 5  # 最近5个交易日，约1200条记录
                elif params['period'] == "5":  # 5分钟  
                    default_max_days = 10  # 最近10个交易日，约480条记录
                else:  # 15分钟、30分钟、60分钟
                    default_max_days = 15  # 最近15个交易日
                
                # 从end_date向前推算，确保时间列存在且为datetime类型
                if '时间' in result_df.columns and len(result_df) > 0:
                    # 确保时间列是datetime类型
                    result_df['时间'] = pd.to_datetime(result_df['时间'])
                    
                    # 获取数据中的最大日期和最小日期
                    end_date_actual = result_df['时间'].max()
                    start_date_actual = result_df['时间'].min()
                    
                    # 计算用户实际的时间范围（天数）
                    user_days = (end_date_actual - start_date_actual).days
                    
                    # 如果用户输入的时间范围小于默认值，按用户输入为准
                    if user_days <= default_max_days * 1.5:  # 考虑周末，用1.5倍系数
                        # 用户时间范围小于等于默认值，不进行限制
                        pass
                    else:
                        # 用户时间范围大于默认值，按股票分析惯例进行限制
                        start_date_limit = end_date_actual - pd.Timedelta(days=default_max_days * 1.5)
                        
                        # 筛选在时间范围内的数据
                        original_len = len(result_df)
                        result_df = result_df[result_df['时间'] >= start_date_limit].copy()
                        
                        # 静默限制数据，不显示提示信息
                        pass
            
            # 输出结果 - 使用兼容的Markdown格式
            yield from self._output_compatible_markdown(result_df)
            context.add_step("历史指标输出", success=True)
        
        except StockDataError:
            raise
        except Exception as e:
            raise CalculationError(
                message=f"历史指标计算错误: {str(e)}",
                indicator_type=params['indicator'],
                details={'symbol': params['symbol'], 'error': str(e)}
            )
    
    def _output_compatible_markdown(self, df: pd.DataFrame) -> Generator[ToolInvokeMessage]:
        """输出兼容的Markdown表格格式，确保与Markdown转XLSX节点兼容"""
        try:
            if df.empty:
                yield self.create_text_message("暂无数据")
                yield self.create_json_message({"data": []})
                return
            
            # 预处理数据，确保数值格式正确
            df_clean = df.copy()
            
            # 处理数值列，避免科学计数法
            for col in df_clean.columns:
                if df_clean[col].dtype in ['float64', 'float32']:
                    # 对于数值列，格式化为固定小数位数，避免科学计数法
                    df_clean[col] = df_clean[col].apply(lambda x: self._format_number(x))
                else:
                    # 其他列转换为字符串
                    df_clean[col] = df_clean[col].astype(str)
            
            # 生成兼容的Markdown表格
            markdown_text = self._generate_compatible_markdown_table(df_clean)
            
            # 输出文本和JSON
            yield self.create_text_message(markdown_text)
            yield self.create_json_message({"data": df_clean.to_dict('records')})
            
        except Exception as e:
            logging.error(f"Error generating compatible markdown: {e}")
            # 回退到标准输出
            yield from process_dataframe_output(df, self)
    
    def _format_number(self, x):
        """格式化数字，避免科学计数法"""
        if pd.isna(x):
            return ""
        
        # 如果是科学计数法，转换为普通数字
        if isinstance(x, (int, float)):
            if abs(x) < 1e-6 and x != 0:
                return f"{x:.8f}"
            elif abs(x) < 1e6:
                return f"{x:.4f}"
            else:
                return f"{x:.0f}"
        else:
            return str(x)
    
    def _generate_compatible_markdown_table(self, df: pd.DataFrame) -> str:
        """生成兼容的Markdown表格格式"""
        if df.empty:
            return "暂无数据"
        
        # 获取列名
        columns = df.columns.tolist()
        
        # 构建表头 - 确保格式完全符合标准
        markdown = "| " + " | ".join(columns) + " |\n"
        markdown += "| " + " | ".join(["---"] * len(columns)) + " |\n"
        
        # 构建数据行
        for idx, row in df.iterrows():
            row_data = []
            for col in columns:
                value = row[col]
                # 处理NaN值
                if pd.isna(value) or value == 'nan' or value == '':
                    value = ""
                else:
                    value = str(value)
                    # 清理特殊字符，确保Markdown兼容
                    value = value.replace('|', '\\|')  # 转义管道符
                    value = value.replace('\n', ' ')   # 替换换行符
                    value = value.replace('\r', ' ')   # 替换回车符
                    value = value.replace('\t', ' ')   # 替换制表符
                    # 确保值不为空
                    if value.strip() == '':
                        value = ""
                row_data.append(value)
            markdown += "| " + " | ".join(row_data) + " |\n"
        
        return markdown
