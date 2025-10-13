"""
估值指标计算器模块
提供动态估值和历史估值指标的计算功能
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from managers.api_manager import APIManager


class ValuationIndicatorCalculator:
    """估值指标计算器"""
    
    def __init__(self, symbol: str, retries: int = 5, timeout: float = 600):
        self.symbol = symbol
        self.retries = retries
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        self.api_manager = APIManager(retries, timeout)
    
    def calculate_dynamic_valuation(self) -> Dict[str, Any]:
        """计算动态估值指标"""
        try:
            # 使用并行调用优化性能
            financial_data, current_price_data = self.api_manager.parallel_financial_calls(self.symbol)
            
            if financial_data is None or financial_data.empty:
                return {"error": "无法获取财务数据"}
            
            if current_price_data is None or current_price_data.empty:
                return {"error": "无法获取当前股价"}
            
            # 获取最新年度数据（优先12月31日）
            annual_data = financial_data[financial_data['日期'].str.contains('12-31', na=False)]
            if not annual_data.empty:
                latest_financial = annual_data.iloc[-1]
                data_type = "年度数据"
            else:
                latest_financial = financial_data.iloc[-1]
                data_type = "最新数据"
            
            current_price = current_price_data.iloc[0]['最新价']
            
            # 计算动态估值指标
            valuation_indicators = self._calculate_valuation_metrics(latest_financial, current_price)
            
            # 添加元数据
            valuation_indicators['当前股价'] = current_price
            valuation_indicators['数据时间点'] = latest_financial['日期'].strftime('%Y-%m-%d') if hasattr(latest_financial['日期'], 'strftime') else str(latest_financial['日期'])
            valuation_indicators['数据类型'] = data_type
            
            return valuation_indicators
            
        except Exception as e:
            self.logger.error(f"计算动态估值指标失败: {e}")
            return {"error": f"计算动态估值指标失败: {str(e)}"}
    
    def calculate_historical_valuation(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算历史估值指标"""
        try:
            # 使用缓存机制优化性能
            financial_cache = self.api_manager.get_financial_cache(self.symbol, "2020")
            
            if not financial_cache:
                self.logger.warning("无法获取财务数据，返回原始历史数据")
                return df
            
            # 预处理数据
            result_df = df.copy()
            
            # 初始化所有历史估值指标列
            self._initialize_valuation_columns(result_df)
            
            self.logger.info(f"找到 {len(financial_cache)} 个年报数据：{list(financial_cache.keys())}")
            
            # 遍历每个交易日，使用缓存的财务数据
            for index, row in result_df.iterrows():
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
                
                # 计算历史估值指标
                self._calculate_historical_metrics_for_row(result_df, index, current_price, financial_data_row)
            
            return result_df
            
        except Exception as e:
            self.logger.error(f"计算历史估值指标失败: {e}")
            return df
    
    def _calculate_valuation_metrics(self, financial_row: pd.Series, current_price: float) -> Dict[str, Any]:
        """计算估值指标"""
        valuation_indicators = {}
        
        # 基础估值指标（处理极限情况）
        eps = pd.to_numeric(financial_row['摊薄每股收益(元)'], errors='coerce')
        if pd.notna(eps) and eps > 0.01:
            valuation_indicators['PE_动态'] = round(current_price / eps, 2)
        elif pd.notna(eps) and eps <= 0:
            valuation_indicators['PE_动态'] = "N/A (负收益或零收益)"
        else:
            valuation_indicators['PE_动态'] = "N/A"
        
        bps = pd.to_numeric(financial_row['每股净资产_调整前(元)'], errors='coerce')
        if pd.notna(bps) and bps > 0.01:
            valuation_indicators['PB_动态'] = round(current_price / bps, 2)
        elif pd.notna(bps) and bps <= 0:
            valuation_indicators['PB_动态'] = "N/A (负净资产)"
        else:
            valuation_indicators['PB_动态'] = "N/A"
        
        cps = pd.to_numeric(financial_row['每股经营性现金流(元)'], errors='coerce')
        if pd.notna(cps) and cps > 0.01:
            valuation_indicators['PCF_动态'] = round(current_price / cps, 2)
        elif pd.notna(cps) and cps <= 0:
            valuation_indicators['PCF_动态'] = "N/A (负现金流)"
        else:
            valuation_indicators['PCF_动态'] = "N/A"
        
        # 扩展估值指标
        w_eps = pd.to_numeric(financial_row['加权每股收益(元)'], errors='coerce')
        if pd.notna(w_eps) and w_eps > 0.01:
            valuation_indicators['PE_加权'] = round(current_price / w_eps, 2)
        elif pd.notna(w_eps) and w_eps <= 0:
            valuation_indicators['PE_加权'] = "N/A (负收益或零收益)"
        else:
            valuation_indicators['PE_加权'] = "N/A"
        
        n_eps = pd.to_numeric(financial_row['扣除非经常性损益后的每股收益(元)'], errors='coerce')
        if pd.notna(n_eps) and n_eps > 0.01:
            valuation_indicators['PE_扣非'] = round(current_price / n_eps, 2)
        elif pd.notna(n_eps) and n_eps <= 0:
            valuation_indicators['PE_扣非'] = "N/A (负收益或零收益)"
        else:
            valuation_indicators['PE_扣非'] = "N/A"
        
        adj_bps = pd.to_numeric(financial_row['每股净资产_调整后(元)'], errors='coerce')
        if pd.notna(adj_bps) and adj_bps > 0.01:
            valuation_indicators['PB_调整后'] = round(current_price / adj_bps, 2)
        elif pd.notna(adj_bps) and adj_bps <= 0:
            valuation_indicators['PB_调整后'] = "N/A (负净资产)"
        else:
            valuation_indicators['PB_调整后'] = "N/A"
        
        # 每股价值指标
        cap_reserve = pd.to_numeric(financial_row['每股资本公积金(元)'], errors='coerce')
        if pd.notna(cap_reserve) and cap_reserve > 0.01:
            valuation_indicators['每股资本公积金比率'] = round(current_price / cap_reserve, 2)
        elif pd.notna(cap_reserve) and cap_reserve <= 0:
            valuation_indicators['每股资本公积金比率'] = "N/A (负值或零值)"
        else:
            valuation_indicators['每股资本公积金比率'] = "N/A"
        
        undist_profit = pd.to_numeric(financial_row['每股未分配利润(元)'], errors='coerce')
        if pd.notna(undist_profit) and undist_profit > 0.01:
            valuation_indicators['每股未分配利润比率'] = round(current_price / undist_profit, 2)
        elif pd.notna(undist_profit) and undist_profit <= 0:
            valuation_indicators['每股未分配利润比率'] = "N/A (负值或零值)"
        else:
            valuation_indicators['每股未分配利润比率'] = "N/A"
        
        # 成长性估值指标
        growth_rate = pd.to_numeric(financial_row['净利润增长率(%)'], errors='coerce')
        if (pd.notna(growth_rate) and growth_rate > 0.01 and 
            'PE_动态' in valuation_indicators and 
            valuation_indicators['PE_动态'] != "N/A" and 
            isinstance(valuation_indicators['PE_动态'], (int, float)) and 
            valuation_indicators['PE_动态'] > 0):
            valuation_indicators['PEG'] = round(valuation_indicators['PE_动态'] / growth_rate, 2)
        else:
            valuation_indicators['PEG'] = "N/A"
        
        # 盈利能力估值指标
        roe = pd.to_numeric(financial_row['净资产收益率(%)'], errors='coerce')
        if (pd.notna(roe) and 
            'PB_动态' in valuation_indicators and 
            valuation_indicators['PB_动态'] != "N/A" and 
            isinstance(valuation_indicators['PB_动态'], (int, float)) and 
            valuation_indicators['PB_动态'] > 0):
            valuation_indicators['市净率×ROE'] = round(valuation_indicators['PB_动态'] * roe, 2)
        else:
            valuation_indicators['市净率×ROE'] = "N/A"
        
        return valuation_indicators
    
    def _initialize_valuation_columns(self, df: pd.DataFrame):
        """初始化历史估值指标列"""
        valuation_columns = [
            'PE_历史', 'PB_历史', 'PCF_历史', 'PE_加权历史', 'PE_扣非历史', 'PB_调整后历史',
            '每股资本公积金比率_历史', '每股未分配利润比率_历史', 'PEG_历史', '市净率×ROE_历史',
            '财务数据时间点'
        ]
        
        for col in valuation_columns:
            df[col] = "N/A"
    
    def _calculate_historical_metrics_for_row(self, df: pd.DataFrame, index: int, 
                                            current_price: float, financial_data_row: Dict):
        """为单行计算历史估值指标"""
        # 基础估值指标
        eps = financial_data_row['eps']
        if pd.notna(eps) and eps > 0.01:
            df.loc[index, 'PE_历史'] = str(round(current_price / eps, 2))
        else:
            df.loc[index, 'PE_历史'] = "N/A"
        
        bps = financial_data_row['bps']
        if pd.notna(bps) and bps > 0.01:
            df.loc[index, 'PB_历史'] = str(round(current_price / bps, 2))
        else:
            df.loc[index, 'PB_历史'] = "N/A"
        
        cps = financial_data_row['cps']
        if pd.notna(cps) and cps > 0.01:
            df.loc[index, 'PCF_历史'] = str(round(current_price / cps, 2))
        else:
            df.loc[index, 'PCF_历史'] = "N/A"
        
        # 扩展估值指标
        w_eps = financial_data_row['w_eps']
        if pd.notna(w_eps) and w_eps > 0.01:
            df.loc[index, 'PE_加权历史'] = str(round(current_price / w_eps, 2))
        else:
            df.loc[index, 'PE_加权历史'] = "N/A"
        
        n_eps = financial_data_row['n_eps']
        if pd.notna(n_eps) and n_eps > 0.01:
            df.loc[index, 'PE_扣非历史'] = str(round(current_price / n_eps, 2))
        else:
            df.loc[index, 'PE_扣非历史'] = "N/A"
        
        adj_bps = financial_data_row['adj_bps']
        if pd.notna(adj_bps) and adj_bps > 0.01:
            df.loc[index, 'PB_调整后历史'] = str(round(current_price / adj_bps, 2))
        else:
            df.loc[index, 'PB_调整后历史'] = "N/A"
        
        # 每股价值指标
        cap_reserve = financial_data_row['cap_reserve']
        if pd.notna(cap_reserve) and cap_reserve > 0.01:
            df.loc[index, '每股资本公积金比率_历史'] = str(round(current_price / cap_reserve, 2))
        else:
            df.loc[index, '每股资本公积金比率_历史'] = "N/A"
        
        undist_profit = financial_data_row['undist_profit']
        if pd.notna(undist_profit) and undist_profit > 0.01:
            df.loc[index, '每股未分配利润比率_历史'] = str(round(current_price / undist_profit, 2))
        else:
            df.loc[index, '每股未分配利润比率_历史'] = "N/A"
        
        # 成长性估值指标
        growth_rate = financial_data_row['growth_rate']
        if (pd.notna(growth_rate) and growth_rate > 0.01 and 
            df.loc[index, 'PE_历史'] != "N/A" and 
            isinstance(df.loc[index, 'PE_历史'], str) and df.loc[index, 'PE_历史'].replace('.', '').isdigit()):
            pe_value = float(df.loc[index, 'PE_历史'])
            if pe_value > 0:
                df.loc[index, 'PEG_历史'] = str(round(pe_value / growth_rate, 2))
            else:
                df.loc[index, 'PEG_历史'] = "N/A"
        else:
            df.loc[index, 'PEG_历史'] = "N/A"
        
        # 盈利能力估值指标
        roe = financial_data_row['roe']
        if (pd.notna(roe) and 
            df.loc[index, 'PB_历史'] != "N/A" and 
            isinstance(df.loc[index, 'PB_历史'], str) and df.loc[index, 'PB_历史'].replace('.', '').isdigit()):
            pb_value = float(df.loc[index, 'PB_历史'])
            if pb_value > 0:
                df.loc[index, '市净率×ROE_历史'] = str(round(pb_value * roe, 2))
            else:
                df.loc[index, '市净率×ROE_历史'] = "N/A"
        else:
            df.loc[index, '市净率×ROE_历史'] = "N/A"
        
        # 添加财务数据时间点信息
        df.loc[index, '财务数据时间点'] = financial_data_row['date'].strftime('%Y-%m-%d')
