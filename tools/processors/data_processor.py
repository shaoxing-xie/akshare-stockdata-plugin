"""
数据处理模块
提供数据预处理、后处理和验证功能
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import logging


class DataProcessor:
    """数据处理器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def preprocess_stock_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        预处理股票数据
        统一处理数据类型转换、排序等操作
        """
        try:
            df = df.copy()
            
            # 确保数值列为正确的数据类型
            numeric_columns = ['开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 确保数据按日期排序
            if '日期' in df.columns:
                df['日期'] = pd.to_datetime(df['日期'])
                df = df.sort_values('日期').reset_index(drop=True)
            
            return df
            
        except Exception as e:
            self.logger.error(f"数据预处理失败: {e}")
            raise
    
    def optimize_memory_usage(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        优化DataFrame内存使用
        """
        try:
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
            
        except Exception as e:
            self.logger.error(f"内存优化失败: {e}")
            return df
    
    def validate_data_quality(self, df: pd.DataFrame, required_columns: List[str] = None) -> Tuple[bool, List[str]]:
        """
        验证数据质量
        返回验证结果和错误信息列表
        """
        errors = []
        
        try:
            # 检查数据是否为空
            if df.empty:
                errors.append("数据为空")
                return False, errors
            
            # 检查必需列是否存在
            if required_columns:
                missing_columns = set(required_columns) - set(df.columns)
                if missing_columns:
                    errors.append(f"缺少必要列: {list(missing_columns)}")
            
            # 检查关键数值列的数据质量
            key_columns = ['收盘', '最高', '最低', '开盘']
            for col in key_columns:
                if col in df.columns:
                    # 检查是否有负值（价格不应为负）
                    if (df[col] < 0).any():
                        errors.append(f"列 {col} 包含负值")
                    
                    # 检查是否有异常大的值
                    if (df[col] > 10000).any():
                        errors.append(f"列 {col} 包含异常大的值")
            
            # 检查日期列的连续性
            if '日期' in df.columns:
                date_col = pd.to_datetime(df['日期'])
                if not date_col.is_monotonic_increasing:
                    errors.append("日期列不是单调递增的")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"数据验证过程出错: {e}")
            return False, errors
    
    def handle_missing_values(self, df: pd.DataFrame, strategy: str = 'preserve_nan') -> pd.DataFrame:
        """
        处理缺失值
        """
        try:
            if strategy == 'preserve_nan':
                # 保持NaN值，用于技术指标
                return df
            elif strategy == 'forward_fill':
                # 前向填充，用于价格数据
                return df.fillna(method='ffill')
            elif strategy == 'interpolate':
                # 插值填充
                return df.interpolate()
            elif strategy == 'drop':
                # 删除包含缺失值的行
                return df.dropna()
            else:
                return df
                
        except Exception as e:
            self.logger.error(f"缺失值处理失败: {e}")
            return df
    
    def standardize_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        标准化数据类型
        """
        try:
            df = df.copy()
            
            # 确保数值列为正确的数据类型
            numeric_columns = ['开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅', '涨跌额', '换手率']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 确保日期列格式正确
            if '日期' in df.columns:
                df['日期'] = pd.to_datetime(df['日期'])
            
            return df
            
        except Exception as e:
            self.logger.error(f"数据类型标准化失败: {e}")
            return df
    
    def process_large_dataset_in_chunks(self, df: pd.DataFrame, chunk_size: int = 1000, 
                                      process_func=None) -> pd.DataFrame:
        """
        分批处理大数据集
        """
        try:
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
            
        except Exception as e:
            self.logger.error(f"分批处理失败: {e}")
            return df
    
    def format_output_data(self, df: pd.DataFrame, indicator_type: str) -> pd.DataFrame:
        """
        格式化输出数据
        """
        try:
            df = df.copy()
            
            # 确保日期列是字符串格式以避免JSON序列化问题
            if '日期' in df.columns:
                df['日期'] = df['日期'].dt.strftime('%Y-%m-%d')
            
            # 确保所有列都是JSON序列化兼容的类型
            df = self._ensure_json_serializable(df)
            
            return df
            
        except Exception as e:
            self.logger.error(f"输出格式化失败: {e}")
            return df
    
    def _ensure_json_serializable(self, df: pd.DataFrame) -> pd.DataFrame:
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
            self.logger.error(f"JSON序列化兼容性处理失败: {e}")
            return df
