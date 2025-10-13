"""
基本信息聚合器模块
提供个股基本信息的聚合功能
"""
import pandas as pd
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from managers.api_manager import APIManager


class BasicInfoAggregator:
    """基本信息聚合器"""
    
    def __init__(self, symbol: str, retries: int = 5, timeout: float = 600):
        self.symbol = symbol
        self.retries = retries
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        self.api_manager = APIManager(retries, timeout)
    
    def aggregate_basic_info(self) -> Dict[str, Any]:
        """聚合基本信息"""
        try:
            summary = self._initialize_summary_structure()
            
            # 使用并行调用优化性能
            api_results = self.api_manager.parallel_basic_info_calls(self.symbol)
            
            # 处理基础股票信息
            self._process_basic_info(summary, api_results.get('basic_info'))
            
            # 处理公司基本信息
            self._process_company_info(summary, api_results.get('company_info'))
            
            # 处理主营业务信息
            self._process_business_info(summary, api_results.get('business_info'))
            
            # 处理业务构成信息
            self._process_business_structure(summary)
            
            # 设置数据更新时间
            summary["元数据"]["数据更新时间"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            return summary
            
        except Exception as e:
            self.logger.error(f"聚合基本信息失败: {e}")
            return {"error": f"聚合基本信息失败: {str(e)}"}
    
    def _initialize_summary_structure(self) -> Dict[str, Any]:
        """初始化汇总结构"""
        return {
            # 1. 股票身份识别
            "股票身份": {
                "股票代码": "",
                "股票简称": "",
                "公司全称": "",
                "所属市场": "",
                "所属行业": ""
            },
            
            # 2. 当前状态
            "当前状态": {
                "最新价格": "",
                "总市值": "",
                "流通市值": "",
                "总股本": "",
                "流通股": ""
            },
            
            # 3. 公司概况
            "公司概况": {
                "成立时间": "",
                "上市时间": "",
                "法人代表": "",
                "注册地址": "",
                "办公地址": "",
                "官方网站": "",
                "联系方式": ""
            },
            
            # 4. 业务描述
            "业务描述": {
                "主营业务": "",
                "产品服务": "",
                "经营范围": "",
                "业务构成": ""
            },
            
            # 5. 元数据
            "元数据": {
                "数据更新时间": "",
                "数据来源": "AKShare",
                "接口状态": {}
            }
        }
    
    def _process_basic_info(self, summary: Dict[str, Any], basic_info: Optional[pd.DataFrame]):
        """处理基础股票信息"""
        try:
            if basic_info is not None and not basic_info.empty:
                # 转换为字典格式便于查找
                basic_dict = dict(zip(basic_info['item'], basic_info['value']))
                
                summary["股票身份"]["股票代码"] = str(basic_dict.get('股票代码', ''))
                summary["股票身份"]["股票简称"] = str(basic_dict.get('股票简称', ''))
                summary["股票身份"]["所属行业"] = str(basic_dict.get('行业', ''))
                
                summary["当前状态"]["最新价格"] = str(basic_dict.get('最新', ''))
                summary["当前状态"]["总市值"] = str(basic_dict.get('总市值', ''))
                summary["当前状态"]["流通市值"] = str(basic_dict.get('流通市值', ''))
                summary["当前状态"]["总股本"] = str(basic_dict.get('总股本', ''))
                summary["当前状态"]["流通股"] = str(basic_dict.get('流通股', ''))
                
                summary["元数据"]["接口状态"]["stock_individual_info_em"] = "成功"
            else:
                summary["元数据"]["接口状态"]["stock_individual_info_em"] = "失败"
                
        except Exception as e:
            self.logger.warning(f"处理基础股票信息失败: {e}")
            summary["元数据"]["接口状态"]["stock_individual_info_em"] = f"错误: {str(e)}"
    
    def _process_company_info(self, summary: Dict[str, Any], company_info: Optional[pd.DataFrame]):
        """处理公司基本信息"""
        try:
            if company_info is not None and not company_info.empty:
                company_row = company_info.iloc[0]
                
                summary["股票身份"]["公司全称"] = str(company_row.get('公司名称', ''))
                summary["股票身份"]["所属市场"] = str(company_row.get('所属市场', ''))
                
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
                
        except Exception as e:
            self.logger.warning(f"处理公司基本信息失败: {e}")
            summary["元数据"]["接口状态"]["stock_profile_cninfo"] = f"错误: {str(e)}"
    
    def _process_business_info(self, summary: Dict[str, Any], business_info: Optional[pd.DataFrame]):
        """处理主营业务信息"""
        try:
            if business_info is not None and not business_info.empty:
                business_row = business_info.iloc[0]
                
                summary["业务描述"]["主营业务"] = str(business_row.get('主营业务', ''))
                summary["业务描述"]["经营范围"] = str(business_row.get('经营范围', ''))
                
                # 组合产品服务信息
                product_type = str(business_row.get('产品类型', ''))
                product_name = str(business_row.get('产品名称', ''))
                product_info = []
                if product_type and product_type != 'nan':
                    product_info.append(f"产品类型: {product_type}")
                if product_name and product_name != 'nan':
                    product_info.append(f"产品名称: {product_name}")
                summary["业务描述"]["产品服务"] = "；".join(product_info) if product_info else ""
                
                summary["元数据"]["接口状态"]["stock_zyjs_ths"] = "成功"
            else:
                summary["元数据"]["接口状态"]["stock_zyjs_ths"] = "失败"
                
        except Exception as e:
            self.logger.warning(f"处理主营业务信息失败: {e}")
            summary["元数据"]["接口状态"]["stock_zyjs_ths"] = f"错误: {str(e)}"
    
    def _process_business_structure(self, summary: Dict[str, Any]):
        """处理业务构成信息"""
        try:
            business_structure = self.api_manager.get_business_structure_data(self.symbol)
            
            if business_structure is not None and not business_structure.empty:
                structure_info = self._extract_business_structure(business_structure)
                summary["业务描述"]["业务构成"] = structure_info
                summary["元数据"]["接口状态"]["stock_zygc_em"] = "成功"
            else:
                summary["业务描述"]["业务构成"] = "N/A (接口无数据)"
                summary["元数据"]["接口状态"]["stock_zygc_em"] = "失败"
                
        except Exception as e:
            # 特殊处理'zygcfx'错误和其他错误
            if "'zygcfx'" in str(e):
                summary["业务描述"]["业务构成"] = "N/A (接口数据结构变更)"
                summary["元数据"]["接口状态"]["stock_zygc_em"] = "接口数据结构变更"
            else:
                summary["业务描述"]["业务构成"] = "N/A"
                summary["元数据"]["接口状态"]["stock_zygc_em"] = f"错误: {str(e)}"
    
    def _extract_business_structure(self, business_structure_df: pd.DataFrame) -> str:
        """提取业务构成信息"""
        if business_structure_df is None or business_structure_df.empty:
            return "N/A"
        
        try:
            # 1. 只取最新的报告期数据
            latest_data = business_structure_df.iloc[0]
            
            # 2. 按分类类型分别处理
            product_data = business_structure_df[
                business_structure_df['分类类型'] == '按产品分类'
            ].iloc[0] if not business_structure_df[
                business_structure_df['分类类型'] == '按产品分类'
            ].empty else None
            
            region_data = business_structure_df[
                business_structure_df['分类类型'] == '按地区分类'
            ].iloc[0] if not business_structure_df[
                business_structure_df['分类类型'] == '按地区分类'
            ].empty else None
            
            # 3. 构建业务构成描述
            structure_info = []
            
            if product_data is not None:
                product_name = str(product_data.get('主营构成', ''))
                income_ratio = product_data.get('收入比例', 0)
                if product_name and product_name != 'nan' and pd.notna(income_ratio):
                    structure_info.append(f"主要产品：{product_name} (收入占比{income_ratio:.1%})")
            
            if region_data is not None:
                region_name = str(region_data.get('主营构成', ''))
                income_ratio = region_data.get('收入比例', 0)
                if region_name and region_name != 'nan' and pd.notna(income_ratio):
                    structure_info.append(f"主要地区：{region_name} (收入占比{income_ratio:.1%})")
            
            return "；".join(structure_info) if structure_info else "N/A"
            
        except Exception as e:
            self.logger.warning(f"提取业务构成信息失败: {e}")
            return "N/A"
    
    def format_basic_info_as_table(self, summary_data: Dict[str, Any]) -> str:
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
