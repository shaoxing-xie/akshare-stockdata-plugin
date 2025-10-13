"""
API管理模块
提供API调用管理和并行处理功能
"""
import concurrent.futures
import pandas as pd
from typing import Dict, Any, Tuple, Optional, List
import logging
import akshare as ak
from functools import lru_cache

from provider.akshare_stockdata import safe_ak_call


class APIManager:
    """API管理器"""
    
    def __init__(self, retries: int = 5, timeout: float = 600):
        self.retries = retries
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
    
    def parallel_basic_info_calls(self, symbol: str) -> Dict[str, Any]:
        """
        并行调用基本信息相关接口
        """
        try:
            def call_api(api_func, **kwargs):
                return safe_ak_call(api_func, retries=self.retries, timeout=self.timeout, **kwargs)
            
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
                        results[name] = future.result(timeout=self.timeout)
                    except Exception as e:
                        results[name] = None
                        self.logger.warning(f"API调用失败 {name}: {e}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"并行基本信息调用失败: {e}")
            return {}
    
    def parallel_financial_calls(self, symbol: str) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """
        并行获取财务数据和当前股价
        """
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                # 并行获取财务数据和当前股价
                financial_future = executor.submit(
                    safe_ak_call, 
                    ak.stock_financial_analysis_indicator,
                    retries=self.retries,
                    timeout=self.timeout,
                    symbol=symbol,
                    start_year="2020"
                )
                
                price_future = executor.submit(
                    safe_ak_call,
                    ak.stock_bid_ask_em,
                    retries=self.retries,
                    timeout=self.timeout,
                    symbol=symbol
                )
                
                # 等待结果
                financial_data = financial_future.result(timeout=self.timeout)
                current_price_data = price_future.result(timeout=self.timeout)
                return financial_data, current_price_data
                
        except Exception as e:
            self.logger.error(f"并行财务数据调用失败: {e}")
            return None, None
    
    @lru_cache(maxsize=128)
    def get_financial_cache(self, symbol: str, start_year: str = "2020") -> Dict[int, Dict]:
        """
        获取财务数据缓存
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
            self.logger.error(f"获取财务数据缓存失败: {e}")
            return {}
    
    def get_historical_data(self, symbol: str, start_date: str, end_date: str, 
                          adjust: str = "qfq") -> Optional[pd.DataFrame]:
        """
        获取历史数据
        """
        try:
            result = safe_ak_call(
                ak.stock_zh_a_hist,
                retries=self.retries,
                timeout=self.timeout,
                symbol=symbol,
                period='daily',
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )
            return result
            
        except Exception as e:
            self.logger.error(f"获取历史数据失败: {e}")
            return None
    
    def get_business_structure_data(self, symbol: str) -> Optional[pd.DataFrame]:
        """
        获取业务构成数据
        """
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
            
            result = safe_ak_call(
                ak.stock_zygc_em,
                retries=2,
                timeout=self.timeout,
                symbol=market_symbol
            )
            return result
            
        except Exception as e:
            self.logger.warning(f"获取业务构成数据失败: {e}")
            return None
    
    def clear_cache(self):
        """
        清除缓存
        """
        self.get_financial_cache.cache_clear()
        self.logger.info("API缓存已清除")
