"""
AKShare Eastmoney接口注册表
管理东方财富股票数据接口的配置信息
"""
import akshare as ak
from typing import Dict, Any, Callable, List, Optional


def normalize_symbol(symbol: str) -> str:
    """标准化股票代码，支持多种格式输入"""
    if not symbol:
        return ""
    
    # 提取数字部分
    digits = "".join(ch for ch in str(symbol) if ch.isdigit())
    if not digits:
        return symbol
    
    # 对于 stock_zh_a_hist 等接口，直接返回纯数字格式
    # 因为 AKShare 的股票历史数据接口只接受纯数字格式
    return digits


def normalize_symbol_with_market_prefix(symbol: str) -> str:
    """标准化股票代码为带市场前缀格式（如sh688686、sz000001）"""
    if not symbol:
        return ""
    
    # 提取数字部分
    digits = "".join(ch for ch in str(symbol) if ch.isdigit())
    if not digits:
        return symbol
    
    if len(digits) == 6:
        # A股代码，根据开头数字判断市场
        if digits.startswith(('60', '68')):
            return f"sh{digits}"  # 上海市场
        elif digits.startswith(('00', '30')):
            return f"sz{digits}"  # 深圳市场
        else:
            return digits
    elif len(digits) == 9:
        # B股代码，保持原格式
        return symbol
    else:
        return digits


def normalize_symbol_with_uppercase_prefix(symbol: str) -> str:
    """标准化股票代码为带大写市场前缀格式（如SH601127、SZ000001）"""
    if not symbol:
        return ""
    
    # 提取数字部分
    digits = "".join(ch for ch in str(symbol) if ch.isdigit())
    if not digits:
        return symbol
    
    if len(digits) == 6:
        # A股代码，根据开头数字判断市场
        if digits.startswith(('60', '68')):
            return f"SH{digits}"  # 上海市场
        elif digits.startswith(('00', '30')):
            return f"SZ{digits}"  # 深圳市场
        else:
            return digits
    elif len(digits) == 9:
        # B股代码，保持原格式
        return symbol
    else:
        return digits


def normalize_symbol_with_dot(symbol: str) -> str:
    """标准化股票代码为带点格式（如301389.SZ）"""
    if not symbol:
        return ""
    
    # 提取数字部分
    digits = "".join(ch for ch in str(symbol) if ch.isdigit())
    if not digits:
        return symbol
    
    if len(digits) == 6:
        # A股代码，根据开头数字判断市场
        if digits.startswith(('60', '68')):
            return f"{digits}.SH"  # 上海市场
        elif digits.startswith(('00', '30')):
            return f"{digits}.SZ"  # 深圳市场
        else:
            return digits
    else:
        return digits


def normalize_us_symbol(symbol: str) -> str:
    """标准化美股股票代码，将常见简称转换为AKShare需要的格式"""
    if not symbol:
        return ""
    
    # 常见美股股票代码映射
    us_symbol_map = {
        "AAPL": "105.AAPL",
        "MSFT": "105.MSFT", 
        "GOOGL": "105.GOOGL",
        "AMZN": "105.AMZN",
        "TSLA": "105.TSLA",
        "META": "105.META",
        "NVDA": "105.NVDA",
        "NFLX": "105.NFLX",
        "TTE": "106.TTE",
        "BABA": "106.BABA",
        "JD": "106.JD",
        "PDD": "106.PDD",
        "NIO": "106.NIO",
        "XPEV": "106.XPEV",
        "LI": "106.LI"
    }
    
    # 如果已经是正确格式（包含点号），直接返回
    if "." in symbol:
        return symbol
    
    # 转换为大写进行匹配
    symbol_upper = symbol.upper()
    
    # 如果在映射表中，返回对应的格式
    if symbol_upper in us_symbol_map:
        return us_symbol_map[symbol_upper]
    
    # 如果不在映射表中，尝试添加默认前缀
    # 大多数美股使用 105 前缀
    return f"105.{symbol_upper}"


def get_symbol_candidates(symbol: str) -> List[str]:
    """获取股票代码的多种候选格式"""
    if not symbol:
        return []
    
    digits = "".join(ch for ch in str(symbol) if ch.isdigit())
    if not digits:
        return [symbol]
    
    if digits.startswith("6"):
        market = "sh"
    else:
        market = "sz"
    
    return [digits, f"{market}{digits}", f"{market.upper()}{digits}"]


# AKShare东方财富接口注册表
REGISTRY: Dict[str, Dict[str, Any]] = {
    "stock_individual_info_em": {
        "label": {"zh_Hans": "东方财富网-股票信息-指定股票", "en_US": "Eastmoney - Stock Information - Specific Stock"},
        "fn": ak.stock_individual_info_em,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-股票信息-指定股票"
    },
    
    "stock_zh_a_hist": {
        "label": {"zh_Hans": "东方财富网-沪深京A股-日频率数据-指定股票、周期、复权方式和指定日期区间", "en_US": "Eastmoney - A-share - Daily Data - Specified Stock, Period, Adjustment and Date Range"},
        "fn": ak.stock_zh_a_hist,
        "params": {
            "required": {
                "symbol": {"type": "str", "preprocess": "normalize_symbol"},
                "period": {"type": "str", "default": "daily"},
                "start_date": {"type": "str", "default": "20240101"},
                "end_date": {"type": "str", "default": "20500101"}
            },
            "optional": {
                "adjust": {"type": "str", "default": ""}
            }
        },
        "supports_timeout": True,
        "description": "东方财富网-沪深京A股-日频率数据-指定股票、周期、复权方式和指定日期区间"
    },
    
    "stock_zh_a_hist_tx": {
        "label": {"zh_Hans": "东方财富网-沪深京A股-历史行情日频率数据-指定股票、复权方式和日期区间", "en_US": "Tencent - A-share - Historical Daily Data - Specified Stock, Adjustment and Date Range"},
        "fn": ak.stock_zh_a_hist_tx,
        "params": {
            "required": {
                "symbol": {"type": "str", "preprocess": "normalize_symbol_with_market_prefix"},
                "start_date": {"type": "str", "default": "19000101"},
                "end_date": {"type": "str", "default": "20500101"}
            },
            "optional": {
                "adjust": {"type": "str", "default": ""},
                "timeout": {"type": "float", "default": None}
            }
        },
        "supports_timeout": True,
        "description": "东方财富网-沪深京A股-历史行情日频率数据-指定股票、复权方式和日期区间"
    },
    
    "stock_zh_a_hist_min_em": {
        "label": {"zh_Hans": "东方财富网-沪深京A股-每日分时行情-指定股票、分时周期、复权方式和日期区间", "en_US": "Eastmoney - A-share - Daily Minute Data - Specified Stock, Minute Period, Adjustment and Date Range"},
        "fn": ak.stock_zh_a_hist_min_em,
        "params": {
            "required": {
                "symbol": {"type": "str", "preprocess": "normalize_symbol"},
                "period": {"type": "str", "default": "5"},
                "start_date": {"type": "str", "default": "20240101"},
                "end_date": {"type": "str", "default": "20500101"}
            },
            "optional": {
                "adjust": {"type": "str", "default": ""}
            }
        },
        "supports_timeout": True,
        "description": "东方财富网-沪深京A股-每日分时行情-指定股票、分时周期、复权方式和日期区间"
    },
    
    "stock_zh_a_hist_pre_min_em": {
        "label": {"zh_Hans": "东方财富网-最近一个交易日-分钟数据(包括盘前)-指定股票、时间区间", "en_US": "Eastmoney - Recent Trading Day - Minute Data (Including Pre-market) - Specified Stock and Time Range"},
        "fn": ak.stock_zh_a_hist_pre_min_em,
        "params": {
            "required": {
                "symbol": {"type": "str", "preprocess": "normalize_symbol"},
                "start_time": {"type": "str", "default": "09:00:00"},
                "end_time": {"type": "str", "default": "15:40:00"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-最近一个交易日-分钟数据(包括盘前)-指定股票、时间区间"
    },
    
    "stock_zh_a_tick_tx": {
        "label": {"zh_Hans": "腾讯财经-最近交易日-历史分笔行情数据-指定股票", "en_US": "Tencent Finance - Recent Trading Day - Historical Tick Data - Specified Stock"},
        "fn": ak.stock_zh_a_tick_tx_js,
        "params": {
            "required": {
                "symbol": {"type": "str", "preprocess": "normalize_symbol_with_market_prefix"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "腾讯财经-最近交易日-历史分笔行情数据-指定股票"
    },
    
    "stock_zh_b_spot_em": {
        "label": {"zh_Hans": "B股实时行情", "en_US": "B-share Real-time Data"},
        "fn": ak.stock_zh_b_spot_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取所有B股上市公司的实时行情数据"
    },
    
    "stock_gsrl_gsdt_em": {
        "label": {"zh_Hans": "东方财富网-公司动态-指定交易日", "en_US": "Eastmoney - Company Dynamics - Specified Trading Day"},
        "fn": ak.stock_gsrl_gsdt_em,
        "params": {
            "required": {"date": {"type": "str", "default": "20240101"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-公司动态-指定交易日"
    },
    
    "stock_zh_a_st_em": {
        "label": {"zh_Hans": "东方财富网-沪深个股-风险警示板", "en_US": "Eastmoney - A-Share Risk Warning Board"},
        "fn": ak.stock_zh_a_st_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-沪深个股-风险警示板"
    },
    
    "stock_zh_a_new_em": {
        "label": {"zh_Hans": "东方财富网-沪深个股-新股板块实时行情", "en_US": "Eastmoney - Shanghai-Shenzhen Individual Stocks - New Stock Board"},
        "fn": ak.stock_zh_a_new_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-沪深个股-新股板块实时行情"
    },
    
    "stock_zh_a_stop_em": {
        "label": {"zh_Hans": "东方财富网-沪深个股-两网及退市", "en_US": "Eastmoney - Shanghai-Shenzhen Individual Stocks - Two Networks & Delisted"},
        "fn": ak.stock_zh_a_stop_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取东方财富网沪深个股两网及退市数据"
    },
    
    "stock_ipo_benefit_ths": {
        "label": {"zh_Hans": "同花顺-新股数据-IPO受益股", "en_US": "THS - IPO Data - IPO Beneficiary Stocks"},
        "fn": ak.stock_ipo_benefit_ths,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取同花顺IPO受益股数据"
    },
    
    "stock_zh_kcb_report_em": {
        "label": {"zh_Hans": "科创板报告", "en_US": "STAR Market Report"},
        "fn": ak.stock_zh_kcb_report_em,
        "params": {
            "required": {},
            "optional": {
                "from_page": {"type": "int", "default": 1},
                "to_page": {"type": "int", "default": 100}
            }
        },
        "supports_timeout": True,
        "description": "获取所有科创板上市公司的报告数据"
    },
    
    "stock_zh_ah_spot_em": {
        "label": {"zh_Hans": "东方财富网-沪深港通-AH股比价-实时行情", "en_US": "Eastmoney - HSGT - AH Stock Comparison - Real-time Quotes"},
        "fn": ak.stock_zh_ah_spot_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-沪深港通-AH股比价-实时行情"
    },
    
    "stock_us_hist": {
        "label": {"zh_Hans": "美股历史数据", "en_US": "US Stock History"},
        "fn": ak.stock_us_hist,
        "params": {
            "required": {
                "symbol": {"type": "str", "preprocess": "normalize_us_symbol"},
                "period": {"type": "str", "default": "daily"},
                "start_date": {"type": "str", "default": "20240101"},
                "end_date": {"type": "str", "default": "20500101"},
                "adjust": {"type": "str", "default": ""}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "获取指定美股上市公司的历史行情数据"
    },
    
    "stock_us_hist_min_em": {
        "label": {"zh_Hans": "美股分钟历史", "en_US": "US Stock Minute History"},
        "fn": ak.stock_us_hist_min_em,
        "params": {
            "required": {
                "symbol": {"type": "str", "preprocess": "normalize_us_symbol"}
            },
            "optional": {
                "start_date": {"type": "str", "default": "1979-09-01 09:32:00"},
                "end_date": {"type": "str", "default": "2222-01-01 09:32:00"}
            }
        },
        "supports_timeout": True,
        "description": "获取指定美股上市公司的分钟级历史数据"
    },
    
    "stock_hk_hist_min_em": {
        "label": {"zh_Hans": "港股分钟历史", "en_US": "HK Stock Minute History"},
        "fn": ak.stock_hk_hist_min_em,
        "params": {
            "required": {
                "symbol": {"type": "str"},
                "period": {"type": "str", "default": "5"},
                "start_date": {"type": "str", "default": "1979-09-01 09:32:00"},
                "end_date": {"type": "str", "default": "2222-01-01 09:32:00"},
                "adjust": {"type": "str", "default": ""}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "获取指定港股上市公司的分钟级历史数据"
    },
    
    # 股市信息总貌相关接口
    "stock_sse_summary": {
        "label": {"zh_Hans": "上交所-股票数据总貌-最近交易日", "en_US": "SSE Stock Data Summary - Latest Trading Day"},
        "fn": ak.stock_sse_summary,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取上海证券交易所股票数据总貌"
    },
    
    "stock_szse_summary": {
        "label": {"zh_Hans": "深交所-证券类别统计-指定交易日", "en_US": "SZSE Securities Category Statistics - Specified Trading Day"},
        "fn": ak.stock_szse_summary,
        "params": {
            "required": {"date": {"type": "str", "default": "20240101"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取深圳证券交易所市场总貌-证券类别统计"
    },
    
    
    "stock_sse_deal_daily": {
        "label": {"zh_Hans": "上交所-股票成交概况-每日股票情况", "en_US": "SSE Stock Trading Overview - Daily Stock Situation"},
        "fn": ak.stock_sse_deal_daily,
        "params": {
            "required": {"date": {"type": "str", "default": "20240101"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "上交所-股票成交概况-每日股票情况"
    },
    
    # 新增的7个股市信息总貌接口
    "stock_gpzy_profile_em": {
        "label": {"zh_Hans": "东方财富网-股权质押市场概况-所有历史", "en_US": "Eastmoney - Equity Pledge Market Overview - All History"},
        "fn": ak.stock_gpzy_profile_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-股权质押市场概况-所有历史"
    },
    
    
    "stock_gpzy_industry_data_em": {
        "label": {"zh_Hans": "东方财富网-上市公司质押比例-行业数据", "en_US": "Eastmoney - Industry Pledge Ratio Data"},
        "fn": ak.stock_gpzy_industry_data_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-上市公司质押比例-行业数据"
    },
    
    "stock_sy_profile_em": {
        "label": {"zh_Hans": "东方财富网-A股商誉市场概况-所有历史", "en_US": "Eastmoney - A-Share Goodwill Market Overview - All History"},
        "fn": ak.stock_sy_profile_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-A股商誉市场概况-所有历史"
    },
    
    "stock_account_statistics_em": {
        "label": {"zh_Hans": "东方财富网-股票账户统计月度-所有历史", "en_US": "Eastmoney - Stock Account Statistics Monthly - All History"},
        "fn": ak.stock_account_statistics_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-股票账户统计月度-所有历史"
    },
    
    "stock_comment_em": {
        "label": {"zh_Hans": "东方财富网-千股千评-所有数据", "en_US": "Eastmoney - Stock Comments - All Data"},
        "fn": ak.stock_comment_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-千股千评-所有数据"
    },
    
    # 资金流向分析相关接口
    "stock_individual_fund_flow": {
        "label": {"zh_Hans": "东方财富网-个股资金流向-指定股票、证交所", "en_US": "East Money - Individual Stock Fund Flow - Specified Stock, Stock Exchange"},
        "fn": ak.stock_individual_fund_flow,
        "params": {
            "required": {
                "stock": {"type": "str"},
                "market": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-个股资金流向-指定股票、市场"
    },
    
    "stock_individual_fund_flow_rank": {
        "label": {"zh_Hans": "东方财富网-资金流向-排名-指定统计周期", "en_US": "East Money - Fund Flow Rankings - Specified Statistical Period"},
        "fn": ak.stock_individual_fund_flow_rank,
        "params": {
            "required": {
                "indicator": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-资金流向-排名-指定统计周期"
    },
    
    "stock_market_fund_flow": {
        "label": {"zh_Hans": "东方财富网-资金流向-大盘-历史数据", "en_US": "East Money - Market Fund Flow - Historical Data"},
        "fn": ak.stock_market_fund_flow,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-资金流向-大盘-历史数据"
    },
    
    "stock_sector_fund_flow_rank": {
        "label": {"zh_Hans": "东方财富网-板块资金流-排名", "en_US": "East Money - Sector Fund Flow Rankings"},
        "fn": ak.stock_sector_fund_flow_rank,
        "params": {
            "required": {
                "indicator": {"type": "str"},
                "sector_type": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-板块资金流-排名"
    },
    
    "stock_fhps_em": {
        "label": {"zh_Hans": "东方财富网-分红配送-指定日期", "en_US": "Eastmoney - Dividend Distribution - Specified Date"},
        "fn": ak.stock_fhps_em,
        "params": {
            "required": {
                "date": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-分红配送-指定日期"
    },
    
    "stock_history_dividend": {
        "label": {"zh_Hans": "新浪财经-历史分红", "en_US": "Sina Finance - Historical Dividend"},
        "fn": ak.stock_history_dividend,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "新浪财经-历史分红"
    },
    
    "stock_info_a_code_name": {
        "label": {"zh_Hans": "沪深京A股-股票代码和简称", "en_US": "All A-Share Stock Codes and Names"},
        "fn": ak.stock_info_a_code_name,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "沪深京A股-股票代码和简称"
    },
    
    "stock_institute_hold": {
        "label": {"zh_Hans": "新浪财经-机构持股一览表-指定报告期", "en_US": "Sina Finance - Institutional Holdings Overview"},
        "fn": ak.stock_institute_hold,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "新浪财经-机构持股一览表-指定报告期"
    },
    
    "stock_institute_recommend": {
        "label": {"zh_Hans": "新浪财经-机构推荐池-指定指标", "en_US": "Sina Finance - Institutional Recommendation Pool - Specific Indicator"},
        "fn": ak.stock_institute_recommend,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "新浪财经-机构推荐池-指定指标"
    },
    
    "stock_main_fund_flow": {
        "label": {"zh_Hans": "东方财富网-主力净流入排名", "en_US": "East Money - Main Fund Flow Rankings"},
        "fn": ak.stock_main_fund_flow,
        "params": {
            "required": {
                "symbol": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-主力净流入排名"
    },
    
    "stock_sector_fund_flow_summary": {
        "label": {"zh_Hans": "东方财富网-行业资金流-xx行业个股资金流", "en_US": "East Money - Sector Fund Flow - Individual Stocks"},
        "fn": ak.stock_sector_fund_flow_summary,
        "params": {
            "required": {
                "symbol": {"type": "str"},
                "indicator": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-行业资金流-xx行业个股资金流"
    },
    
    "stock_sector_fund_flow_hist": {
        "label": {"zh_Hans": "东方财富网-行业历史资金流", "en_US": "East Money - Sector Historical Fund Flow"},
        "fn": ak.stock_sector_fund_flow_hist,
        "params": {
            "required": {
                "symbol": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-行业历史资金流"
    },
    
    "stock_concept_fund_flow_hist": {
        "label": {"zh_Hans": "东方财富网-概念历史资金流", "en_US": "East Money - Concept Historical Fund Flow"},
        "fn": ak.stock_concept_fund_flow_hist,
        "params": {
            "required": {
                "symbol": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-概念历史资金流"
    },
    
    "stock_fund_flow_big_deal": {
        "label": {"zh_Hans": "同花顺-资金流向-大单追踪", "en_US": "Flush - Fund Flow Big Deal Tracking"},
        "fn": ak.stock_fund_flow_big_deal,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "同花顺-资金流向-大单追踪"
    },
    
    "stock_cyq_em": {
        "label": {"zh_Hans": "东方财富网-日K-筹码分布", "en_US": "East Money - Daily K Chip Distribution"},
        "fn": ak.stock_cyq_em,
        "params": {
            "required": {
                "symbol": {"type": "str"},
                "adjust": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-日K-筹码分布"
    },
    
    "stock_fund_flow_individual": {
        "label": {"zh_Hans": "同花顺-个股资金流-指定排行类别", "en_US": "Flush - Individual Stock Fund Flow - Specify Ranking Category"},
        "fn": ak.stock_fund_flow_individual,
        "params": {
            "required": {
                "symbol": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "同花顺-个股资金流-指定排行类别"
    },
    
    "stock_fund_flow_concept": {
        "label": {"zh_Hans": "同花顺-概念资金流-指定排行类别", "en_US": "Flush - Concept Fund Flow - Specify Ranking Category"},
        "fn": ak.stock_fund_flow_concept,
        "params": {
            "required": {
                "symbol": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "同花顺-概念资金流-指定排行类别"
    },
    
    "stock_fund_flow_industry": {
        "label": {"zh_Hans": "同花顺-行业资金流-指定排行类别", "en_US": "Flush - Industry Fund Flow - Specify Ranking Category"},
        "fn": ak.stock_fund_flow_industry,
        "params": {
            "required": {
                "symbol": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "同花顺-行业资金流-指定排行类别"
    },
    
    "stock_hsgt_fund_flow_summary_em": {
        "label": {"zh_Hans": "东方财富网-沪深港通资金流向", "en_US": "East Money - HSGT Fund Flow Summary"},
        "fn": ak.stock_hsgt_fund_flow_summary_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-沪深港通资金流向"
    },
    
    # 沪深港通持股相关接口
    "stock_hk_ggt_components_em": {
        "label": {"zh_Hans": "东方财富网-港股通成份股实时行情", "en_US": "East Money - HK Connect Components Real-time Quotes"},
        "fn": ak.stock_hk_ggt_components_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-港股通成份股实时行情"
    },
    
    "stock_hsgt_fund_min_em": {
        "label": {"zh_Hans": "东方财富网-沪深港通-市场概括-分时数据-指定资金类别", "en_US": "East Money - HSGT Market Overview Minute Data - Specify Fund Category"},
        "fn": ak.stock_hsgt_fund_min_em,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-沪深港通-市场概括-分时数据-指定资金类别"
    },
    
    "stock_hsgt_board_rank_em": {
        "label": {"zh_Hans": "东方财富网-沪深港通持股-板块排行-指定排行类别和统计周期", "en_US": "East Money - HSGT Holdings Board Rankings - Specify Ranking Category and Statistical Period"},
        "fn": ak.stock_hsgt_board_rank_em,
        "params": {
            "required": {
                "symbol": {"type": "str"},
                "indicator": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-沪深港通持股-板块排行-指定排行类别和统计周期"
    },
    
    "stock_hsgt_hold_stock_em": {
        "label": {"zh_Hans": "东方财富网-沪深港通持股-个股排行-指定沪深港通类别和统计周期", "en_US": "East Money - HSGT Holdings Stock Rankings - Specify HSGT Category and Statistical Period"},
        "fn": ak.stock_hsgt_hold_stock_em,
        "params": {
            "required": {
                "market": {"type": "str"},
                "indicator": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-沪深港通持股-个股排行-指定沪深港通类别和统计周期"
    },
    
    "stock_hsgt_sh_hk_spot_em": {
        "label": {"zh_Hans": "东方财富网-港股通(沪>港)-股票实时行情", "en_US": "East Money - HK Connect (Shanghai>HK) Real-time Quotes"},
        "fn": ak.stock_hsgt_sh_hk_spot_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-港股通(沪>港)-股票实时行情"
    },
    
    "stock_hsgt_hist_em": {
        "label": {"zh_Hans": "东方财富网-沪深港通资金流向-历史数据-指定历史数据类别", "en_US": "East Money - HSGT Fund Flow Historical Data - Specify Historical Data Category"},
        "fn": ak.stock_hsgt_hist_em,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-沪深港通资金流向-历史数据-指定历史数据类别"
    },
    
    "stock_hsgt_individual_em": {
        "label": {"zh_Hans": "东方财富网-沪深港通持股-具体股票-指定A股和港股", "en_US": "East Money - HSGT Holdings Specific Stock - Specify A-share and HK Stock"},
        "fn": ak.stock_hsgt_individual_em,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-沪深港通持股-具体股票-指定A股和港股"
    },
    
    # 个股信息总貌相关接口
    "stock_hk_security_profile_em": {
        "label": {"zh_Hans": "港股-个股-证券概况", "en_US": "HK Security Profile"},
        "fn": ak.stock_hk_security_profile_em,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取港股证券概况信息"
    },
    
    "stock_hk_company_profile_em": {
        "label": {"zh_Hans": "港股-个股-公司概况", "en_US": "HK Company Profile"},
        "fn": ak.stock_hk_company_profile_em,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取港股公司概况信息"
    },
    
    "stock_zyjs_ths": {
        "label": {"zh_Hans": "A股-个股-主营业务", "en_US": "A-share Main Business"},
        "fn": ak.stock_zyjs_ths,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "同花顺-主营介绍-指定股票"
    },
    
    "stock_zygc_em": {
        "label": {"zh_Hans": "A股-个股-主营业务", "en_US": "A-share Main Business"},
        "fn": ak.stock_zygc_em,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol_with_uppercase_prefix"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-主营构成-指定股票"
    },
    
    "stock_news_em": {
        "label": {"zh_Hans": "A股-个股-相关新闻资讯", "en_US": "A-share News"},
        "fn": ak.stock_news_em,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-新闻资讯数据-指定股票"
    },
    
    "stock_profile_cninfo": {
        "label": {"zh_Hans": "A股-个股-公司概况", "en_US": "A-share Company Profile"},
        "fn": ak.stock_profile_cninfo,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "巨潮资讯-公司概况-指定股票"
    },
    
    
    "stock_ipo_summary_cninfo": {
        "label": {"zh_Hans": "A股-个股-IPO信息", "en_US": "A-share IPO Info"},
        "fn": ak.stock_ipo_summary_cninfo,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "巨潮资讯-上市相关资讯-指定股票"
    },
    
    "stock_share_change_cninfo": {
        "label": {"zh_Hans": "公司股本变动", "en_US": "Share Change"},
        "fn": ak.stock_share_change_cninfo,
        "params": {
            "required": {
                "symbol": {"type": "str", "preprocess": "normalize_symbol"},
                "start_date": {"type": "str"},
                "end_date": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "巨潮资讯-公司股本变动-指定股票、时间段"
    },
    
    "stock_fhps_detail_em": {
        "label": {"zh_Hans": "A股-个股-分红配股", "en_US": "A-share Dividend"},
        "fn": ak.stock_fhps_detail_em,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-分红送配详情-指定股票"
    },
    
    "stock_fhps_detail_ths": {
        "label": {"zh_Hans": "同花顺-分红情况", "en_US": "THS Dividend Details"},
        "fn": ak.stock_fhps_detail_ths,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "同花顺-分红情况-指定股票"
    },
    
    "stock_dividend_cninfo": {
        "label": {"zh_Hans": "巨潮资讯-历史分红-指定股票", "en_US": "CNINFO - Historical Dividend - Specific Stock"},
        "fn": ak.stock_dividend_cninfo,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "巨潮资讯-历史分红-指定股票"
    },
    
    "stock_hk_fhpx_detail_ths": {
        "label": {"zh_Hans": "港股-个股-分红信息", "en_US": "HK Dividend"},
        "fn": ak.stock_hk_fhpx_detail_ths,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取港股分红信息"
    },
    
    "stock_research_report_em": {
        "label": {"zh_Hans": "A股-个股-研报列表", "en_US": "A-share Research Report"},
        "fn": ak.stock_research_report_em,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-个股研报-指定股票"
    },
    
    
    # 股票财务数据分析相关接口
    "stock_yjbb_em": {
        "label": {"zh_Hans": "东方财富网-业绩报表", "en_US": "East Money - Performance Report"},
        "fn": ak.stock_yjbb_em,
        "params": {
            "required": {
                "date": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-业绩报表"
    },
    
    "stock_yjkb_em": {
        "label": {"zh_Hans": "东方财富网-业绩快报", "en_US": "East Money - Performance Forecast"},
        "fn": ak.stock_yjkb_em,
        "params": {
            "required": {
                "date": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-业绩快报"
    },
    
    "stock_yjyg_em": {
        "label": {"zh_Hans": "东方财富网-业绩预告", "en_US": "East Money - Performance Prediction"},
        "fn": ak.stock_yjyg_em,
        "params": {
            "required": {
                "date": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-业绩预告"
    },
    
    "stock_lrb_em": {
        "label": {"zh_Hans": "东方财富网-业绩快报-利润表", "en_US": "East Money - Performance Report - Profit Statement"},
        "fn": ak.stock_lrb_em,
        "params": {
            "required": {
                "date": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-业绩快报-利润表"
    },
    
    "stock_xjll_em": {
        "label": {"zh_Hans": "东方财富网-业绩快报-现金流量表", "en_US": "East Money - Performance Report - Cash Flow Statement"},
        "fn": ak.stock_xjll_em,
        "params": {
            "required": {
                "date": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-业绩快报-现金流量表"
    },
    
    "stock_zcfz_em": {
        "label": {"zh_Hans": "东方财富网-业绩快报-资产负债表", "en_US": "East Money - Performance Report - Balance Sheet"},
        "fn": ak.stock_zcfz_em,
        "params": {
            "required": {
                "date": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-业绩快报-资产负债表"
    },
    
    "stock_zcfz_bj_em": {
        "label": {"zh_Hans": "东方财富网-北交所-业绩快报-资产负债表", "en_US": "East Money - BJ Exchange - Performance Report - Balance Sheet"},
        "fn": ak.stock_zcfz_bj_em,
        "params": {
            "required": {
                "date": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-北交所-业绩快报-资产负债表"
    },
    
    "stock_financial_report_sina": {
        "label": {"zh_Hans": "新浪财经-财务报表-指定股票、报表类型", "en_US": "Sina Finance - Financial Report - Specify Stock, Report Type"},
        "fn": ak.stock_financial_report_sina,
        "params": {
            "required": {
                "stock": {"type": "str"},
                "symbol": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "新浪财经-财务报表-三大报表"
    },
    
    "stock_balance_sheet_by_report_em": {
        "label": {"zh_Hans": "东方财富网-资产负债表-按报告期-指定股票", "en_US": "Eastmoney - Balance Sheet (by Report Period) - Specific Stock"},
        "fn": ak.stock_balance_sheet_by_report_em,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol_with_uppercase_prefix"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-资产负债表-按报告期-指定股票"
    },
    
    "stock_balance_sheet_by_yearly_em": {
        "label": {"zh_Hans": "东方财富网-资产负债表-按年度-指定股票", "en_US": "Eastmoney - Balance Sheet (by Yearly) - Specific Stock"},
        "fn": ak.stock_balance_sheet_by_yearly_em,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol_with_uppercase_prefix"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-资产负债表-按年度-指定股票"
    },
    
    "stock_profit_sheet_by_report_em": {
        "label": {"zh_Hans": "东方财富网-利润表-按报告期-指定股票", "en_US": "Eastmoney - Profit Sheet (by Report Period) - Specific Stock"},
        "fn": ak.stock_profit_sheet_by_report_em,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol_with_uppercase_prefix"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-利润表-按报告期-指定股票"
    },
    
    "stock_profit_sheet_by_yearly_em": {
        "label": {"zh_Hans": "东方财富网-利润表-按年度-指定股票", "en_US": "Eastmoney - Profit Sheet (by Yearly) - Specific Stock"},
        "fn": ak.stock_profit_sheet_by_yearly_em,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol_with_uppercase_prefix"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-利润表-按年度-指定股票"
    },
    
    "stock_profit_sheet_by_quarterly_em": {
        "label": {"zh_Hans": "东方财富网-利润表-按单季度-指定股票", "en_US": "Eastmoney - Profit Sheet (by Quarterly) - Specific Stock"},
        "fn": ak.stock_profit_sheet_by_quarterly_em,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol_with_uppercase_prefix"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-利润表-按单季度-指定股票"
    },
    
    "stock_cash_flow_sheet_by_report_em": {
        "label": {"zh_Hans": "东方财富网-现金流量表-按报告期-指定股票", "en_US": "Eastmoney - Cash Flow Sheet (by Report Period) - Specific Stock"},
        "fn": ak.stock_cash_flow_sheet_by_report_em,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol_with_uppercase_prefix"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-现金流量表-按报告期-指定股票"
    },
    
    "stock_cash_flow_sheet_by_yearly_em": {
        "label": {"zh_Hans": "东方财富网-现金流量表-按年度-指定股票", "en_US": "Eastmoney - Cash Flow Sheet (by Yearly) - Specific Stock"},
        "fn": ak.stock_cash_flow_sheet_by_yearly_em,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol_with_uppercase_prefix"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-现金流量表-按年度-指定股票"
    },
    
    "stock_cash_flow_sheet_by_quarterly_em": {
        "label": {"zh_Hans": "东方财富网-现金流量表-按单季度-指定股票", "en_US": "Eastmoney - Cash Flow Sheet (by Quarterly) - Specific Stock"},
        "fn": ak.stock_cash_flow_sheet_by_quarterly_em,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol_with_uppercase_prefix"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-现金流量表-按单季度-指定股票"
    },
    
    "stock_financial_debt_ths": {
        "label": {"zh_Hans": "同花顺-资产负债表-指定股票、报告类型", "en_US": "THS - Individual Balance Sheet - By Report Type"},
        "fn": ak.stock_financial_debt_ths,
        "params": {
            "required": {
                "symbol": {"type": "str", "preprocess": "normalize_symbol"},
                "indicator": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "同花顺-资产负债表-指定股票、报告类型"
    },
    
    "stock_financial_benefit_ths": {
        "label": {"zh_Hans": "同花顺-个股利润表-指定股票、报告类型", "en_US": "THS - Individual Income Statement - By Report Type"},
        "fn": ak.stock_financial_benefit_ths,
        "params": {
            "required": {
                "symbol": {"type": "str", "preprocess": "normalize_symbol"},
                "indicator": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "同花顺-个股利润表-指定股票、报告类型"
    },
    
    "stock_financial_cash_ths": {
        "label": {"zh_Hans": "同花顺-现金流量表-指定股票、报告类型", "en_US": "THS - Individual Cash Flow Statement - By Report Type"},
        "fn": ak.stock_financial_cash_ths,
        "params": {
            "required": {
                "symbol": {"type": "str", "preprocess": "normalize_symbol"},
                "indicator": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "同花顺-现金流量表-指定股票、报告类型"
    },
    
    "stock_financial_abstract": {
        "label": {"zh_Hans": "新浪财经-财务报表-关键指标-指定股票", "en_US": "Sina Finance - Financial Statements (Key Indicators) - Specific Stock"},
        "fn": ak.stock_financial_abstract,
        "params": {
            "required": {"symbol": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "新浪财经-财务报表-关键指标-指定股票"
    },
    
    "stock_financial_abstract_ths": {
        "label": {"zh_Hans": "同花顺-财务指标-主要指标-指定股票、指标类型", "en_US": "Flush - Financial Indicators - Main Indicators - Specify Stock, Indicator Type"},
        "fn": ak.stock_financial_abstract_ths,
        "params": {
            "required": {
                "symbol": {"type": "str", "preprocess": "normalize_symbol"},
                "indicator": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "同花顺-财务指标-主要指标-指定股票、指标类型"
    },
    
    "stock_financial_analysis_indicator_em": {
        "label": {"zh_Hans": "东方财富网-A股财务分析-主要指标-指定股票、报告类型", "en_US": "Eastmoney - A-share Financial Analysis (Main Indicators) - By Report Type"},
        "fn": ak.stock_financial_analysis_indicator_em,
        "params": {
            "required": {
                "symbol": {"type": "str", "preprocess": "normalize_symbol_with_dot"},
                "indicator": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-A股财务分析-主要指标-指定股票、报告类型"
    },
    
    "stock_financial_analysis_indicator": {
        "label": {"zh_Hans": "新浪财经-财务分析(财务指标)-指定股票、开始年份", "en_US": "Sina Finance - Financial Analysis (Financial Indicators) - By Report Type"},
        "fn": ak.stock_financial_analysis_indicator,
        "params": {
            "required": {
                "symbol": {"type": "str", "preprocess": "normalize_symbol"},
                "start_year": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "新浪财经-财务分析(财务指标)-指定股票、开始年份"
    },
    
    
    "stock_gdfx_free_top_10_em": {
        "label": {"zh_Hans": "东方财富网-个股-十大流通股东-按日期(季末)", "en_US": "Eastmoney Individual Top 10 Free Shareholders - By Date (Quarter End)"},
        "fn": ak.stock_gdfx_free_top_10_em,
        "params": {
            "required": {
                "symbol": {"type": "str", "preprocess": "normalize_symbol_with_lowercase_prefix"},
                "date": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-个股-十大流通股东-指定股票、日期(季末)"
    },
    
    "stock_gdfx_top_10_em": {
        "label": {"zh_Hans": "东方财富网-个股-十大股东-按日期(季末)", "en_US": "Eastmoney Individual Top 10 Shareholders - By Date (Quarter End)"},
        "fn": ak.stock_gdfx_top_10_em,
        "params": {
            "required": {
                "symbol": {"type": "str", "preprocess": "normalize_symbol_with_lowercase_prefix"},
                "date": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-个股-十大股东-指定股票、日期(季末)"
    },
    
    "stock_gdfx_free_holding_change_em": {
        "label": {"zh_Hans": "东方财富网-个股股东持股变动统计(十大流通股东)-按日期(季末)", "en_US": "Eastmoney Individual Shareholder Holding Change Statistics (Top 10 Free Shareholders) - By Date (Quarter End)"},
        "fn": ak.stock_gdfx_free_holding_change_em,
        "params": {
            "required": {"date": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "获取东方财富网十大流通股东持股变动统计数据"
    },
    
    "stock_gdfx_holding_change_em": {
        "label": {"zh_Hans": "东方财富网-个股股东持股变动统计(十大股东)-按日期(季末)", "en_US": "Eastmoney Individual Shareholder Holding Change Statistics (Top 10 Shareholders) - By Date (Quarter End)"},
        "fn": ak.stock_gdfx_holding_change_em,
        "params": {
            "required": {"date": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "获取东方财富网十大股东持股变动统计数据"
    },
    
    "stock_fund_stock_holder": {
        "label": {"zh_Hans": "新浪财经-基金持股-指定股票", "en_US": "Sina Finance - Fund Shareholding - Specific Stock"},
        "fn": ak.stock_fund_stock_holder,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "新浪财经-基金持股-指定股票"
    },
    
    "stock_main_stock_holder": {
        "label": {"zh_Hans": "新浪财经-主要股东-指定股票", "en_US": "Sina Finance - Major Shareholders - Specific Stock"},
        "fn": ak.stock_main_stock_holder,
        "params": {
            "required": {"stock": {"type": "str", "preprocess": "normalize_symbol"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "新浪财经-主要股东-指定股票"
    },
    
    "stock_institute_hold_detail": {
        "label": {"zh_Hans": "新浪财经-机构持股详情-指定股票、报告期", "en_US": "Sina Finance - Institutional Holdings Detail - Specific Stock and Quarter"},
        "fn": ak.stock_institute_hold_detail,
        "params": {
            "required": {
                "stock": {"type": "str", "preprocess": "normalize_symbol"},
                "quarter": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "新浪财经-机构持股详情-指定股票、报告期"
    },
    
    "stock_institute_recommend_detail": {
        "label": {"zh_Hans": "新浪财经-股票评级记录-指定股票", "en_US": "Sina Finance - Stock Rating Records - Specific Stock"},
        "fn": ak.stock_institute_recommend_detail,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "新浪财经-股票评级记录-指定股票"
    },
    
    "stock_value_em": {
        "label": {"zh_Hans": "东方财富网-估值分析-指定股票", "en_US": "Eastmoney - Valuation Analysis - Specific Stock"},
        "fn": ak.stock_value_em,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-估值分析-指定股票"
    },
    
    "stock_management_change_ths": {
        "label": {"zh_Hans": "同花顺-个股公司高管持股变动-指定股票", "en_US": "THS Individual Company Management Shareholding Change - Specific Stock"},
        "fn": ak.stock_management_change_ths,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "同花顺-公司高管持股变动-指定股票"
    },
    
    "stock_shareholder_change_ths": {
        "label": {"zh_Hans": "同花顺-个股公司股东持股变动-指定股票", "en_US": "THS Individual Company Shareholder Shareholding Change - Specific Stock"},
        "fn": ak.stock_shareholder_change_ths,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "同花顺-公司股东持股变动-指定股票"
    },
    
    "stock_zh_a_gdhs": {
        "label": {"zh_Hans": "东方财富网-股东户数数据-指定日期", "en_US": "Eastmoney - Shareholder Number Data - Specified Date"},
        "fn": ak.stock_zh_a_gdhs,
        "params": {
            "required": {
                "symbol": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-股东户数数据-指定日期"
    },
    
    "stock_zh_a_gdhs_detail_em": {
        "label": {"zh_Hans": "东方财富网-股东户数详情-指定股票", "en_US": "Eastmoney - Shareholder Number Detail - Specific Stock"},
        "fn": ak.stock_zh_a_gdhs_detail_em,
        "params": {
            "required": {
                "symbol": {"type": "str", "preprocess": "normalize_symbol"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-股东户数详情-指定股票"
    },
    
    "stock_ipo_info": {
        "label": {"zh_Hans": "新浪财经-新股发行-指定股票", "en_US": "Sina Finance - IPO Information - Specific Stock"},
        "fn": ak.stock_ipo_info,
        "params": {
            "required": {
                "stock": {"type": "str", "preprocess": "normalize_symbol"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "新浪财经-新股发行-指定股票"
    },
    
    "stock_add_stock": {
        "label": {"zh_Hans": "新浪财经-股票增发-指定股票", "en_US": "Sina Finance - Additional Stock Issuance - Specific Stock"},
        "fn": ak.stock_add_stock,
        "params": {
            "required": {
                "symbol": {"type": "str", "preprocess": "normalize_symbol"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "新浪财经-股票增发-指定股票"
    },
    
    "stock_restricted_release_queue_sina": {
        "label": {"zh_Hans": "新浪财经-限售解禁-指定股票", "en_US": "Sina Finance - Restricted Stock Release Schedule - Specific Stock"},
        "fn": ak.stock_restricted_release_queue_sina,
        "params": {
            "required": {
                "symbol": {"type": "str", "preprocess": "normalize_symbol"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "新浪财经-限售解禁-指定股票"
    },
    
    "stock_gdfx_free_holding_analyse_em": {
        "label": {"zh_Hans": "东方财富网-股东持股分析(十大流通股东)-按日期(季末)", "en_US": "Eastmoney Shareholder Holding Analysis (Top 10 Free Shareholders) - By Date (Quarter End)"},
        "fn": ak.stock_gdfx_free_holding_analyse_em,
        "params": {
            "required": {"date": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "获取东方财富网十大流通股东持股分析数据"
    },
    
    "stock_gdfx_holding_analyse_em": {
        "label": {"zh_Hans": "东方财富网-股东持股分析(十大股东)-按日期(季末)", "en_US": "Eastmoney Shareholder Holding Analysis (Top 10 Shareholders) - By Date (Quarter End)"},
        "fn": ak.stock_gdfx_holding_analyse_em,
        "params": {
            "required": {"date": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "获取东方财富网十大股东持股分析数据"
    },
    
    "stock_gdfx_free_holding_detail_em": {
        "label": {"zh_Hans": "东方财富网-股东持股明细(十大流通股东)-按日期(季末)", "en_US": "Eastmoney Shareholder Holding Details (Top 10 Free Shareholders) - By Date (Quarter End)"},
        "fn": ak.stock_gdfx_free_holding_detail_em,
        "params": {
            "required": {"date": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "获取东方财富网十大流通股东持股明细数据"
    },
    
    "stock_gdfx_holding_detail_em": {
        "label": {"zh_Hans": "东方财富网-股东持股明细(十大股东)-按日期(季末)", "en_US": "Eastmoney Shareholder Holding Details (Top 10 Shareholders) - By Date (Quarter End)"},
        "fn": ak.stock_gdfx_holding_detail_em,
        "params": {
            "required": {
                "date": {"type": "str"},
                "indicator": {"type": "str"},
                "symbol": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "获取东方财富网十大股东持股明细数据"
    },
    
    "stock_gdfx_free_holding_statistics_em": {
        "label": {"zh_Hans": "东方财富网-股东持股统计(十大流通股东)-按日期(季末)", "en_US": "Eastmoney Shareholder Holding Statistics (Top 10 Free Shareholders) - By Date (Quarter End)"},
        "fn": ak.stock_gdfx_free_holding_statistics_em,
        "params": {
            "required": {"date": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "获取东方财富网十大流通股东持股统计数据"
    },
    
    "stock_gdfx_holding_statistics_em": {
        "label": {"zh_Hans": "东方财富网-股东持股统计(十大股东)-按日期(季末)", "en_US": "Eastmoney Shareholder Holding Statistics (Top 10 Shareholders) - By Date (Quarter End)"},
        "fn": ak.stock_gdfx_holding_statistics_em,
        "params": {
            "required": {"date": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "获取东方财富网十大股东持股统计数据"
    },
    
    
    # 股票实时行情相关接口
    "stock_bid_ask_em": {
        "label": {"zh_Hans": "东方财富网-行情报价-指定股票", "en_US": "Eastmoney - Stock Quote - Specific Stock"},
        "fn": ak.stock_bid_ask_em,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-行情报价-指定股票"
    },
    
    "stock_zh_a_spot": {
        "label": {"zh_Hans": "新浪财经-沪深京A股-实时行情数据", "en_US": "Sina Finance - A-share - Real-time Quotes"},
        "fn": ak.stock_zh_a_spot,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "新浪财经-沪深京A股-实时行情数据"
    },
    "stock_zh_a_spot_em": {
        "label": {"zh_Hans": "东方财富网-沪深京A股-实时行情数据", "en_US": "Eastmoney - A-share - Real-time Quotes"},
        "fn": ak.stock_zh_a_spot_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-沪深京A股-实时行情数据"
    },
    
    "stock_sh_a_spot_em": {
        "label": {"zh_Hans": "东方财富网-沪A股-实时行情数据", "en_US": "Eastmoney - Shanghai A-share - Real-time Quotes"},
        "fn": ak.stock_sh_a_spot_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-沪A股-实时行情数据"
    },
    
    "stock_sz_a_spot_em": {
        "label": {"zh_Hans": "东方财富网-深A股-实时行情数据", "en_US": "Eastmoney - Shenzhen A-share - Real-time Quotes"},
        "fn": ak.stock_sz_a_spot_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-深A股-实时行情数据"
    },
    
    "stock_bj_a_spot_em": {
        "label": {"zh_Hans": "东方财富网-京A股-实时行情数据", "en_US": "Eastmoney - Beijing A-share - Real-time Quotes"},
        "fn": ak.stock_bj_a_spot_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-京A股-实时行情数据"
    },
    
    "stock_new_a_spot_em": {
        "label": {"zh_Hans": "东方财富网-新股-实时行情数据", "en_US": "Eastmoney - New Shares - Real-time Quotes"},
        "fn": ak.stock_new_a_spot_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-新股-实时行情数据"
    },
    
    "stock_cy_a_spot_em": {
        "label": {"zh_Hans": "东方财富网-创业板-实时行情", "en_US": "Eastmoney - Growth Enterprise Market - Real-time Quotes"},
        "fn": ak.stock_cy_a_spot_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-创业板-实时行情"
    },
    
    "stock_kc_a_spot_em": {
        "label": {"zh_Hans": "东方财富网-科创板-实时行情", "en_US": "Eastmoney - Science and Technology Innovation Board - Real-time Quotes"},
        "fn": ak.stock_kc_a_spot_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-科创板-实时行情"
    },
    
    "stock_zh_ab_comparison_em": {
        "label": {"zh_Hans": "东方财富网-沪深京A股-全量AB股比价", "en_US": "Eastmoney - Shanghai-Shenzhen - All AB Stock Comparison"},
        "fn": getattr(ak, 'stock_zh_ab_comparison_em', None),
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "东方财富网-沪深京A股-全量AB股比价"
    },
    
    "stock_zh_a_new": {
        "label": {"zh_Hans": "新浪财经-沪深股市-次新股-实时行情", "en_US": "Sina Finance - Shanghai-Shenzhen Stock Market - Secondary New Stocks"},
        "fn": ak.stock_zh_a_new,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "新浪财经-沪深股市-次新股-实时行情"
    },
    
    
    "stock_sgt_settlement_exchange_rate_szse": {
        "label": {"zh_Hans": "深港通-港股通业务信息-结算汇率", "en_US": "SZSE - HK Connect Settlement Exchange Rate"},
        "fn": ak.stock_sgt_settlement_exchange_rate_szse,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "深港通-港股通业务信息-结算汇率"
    },
    
    "stock_sgt_settlement_exchange_rate_sse": {
        "label": {"zh_Hans": "沪港通-港股通信息披露-结算汇兑", "en_US": "SSE - HK Connect Settlement Exchange Rate"},
        "fn": ak.stock_sgt_settlement_exchange_rate_sse,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "沪港通-港股通信息披露-结算汇兑"
    },
    
    "stock_sgt_reference_exchange_rate_szse": {
        "label": {"zh_Hans": "深港通-港股通业务信息-参考汇率", "en_US": "SZSE - HK Connect Reference Exchange Rate"},
        "fn": ak.stock_sgt_reference_exchange_rate_szse,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "深港通-港股通业务信息-参考汇率"
    },
    
    "stock_sgt_reference_exchange_rate_sse": {
        "label": {"zh_Hans": "沪港通-港股通信息披露-参考汇率", "en_US": "SSE - HK Connect Reference Exchange Rate"},
        "fn": ak.stock_sgt_reference_exchange_rate_sse,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "沪港通-港股通信息披露-参考汇率"
    },
    
    "stock_hk_spot_em": {
        "label": {"zh_Hans": "东方财富网-港股-实时行情(延15分钟)", "en_US": "Eastmoney - HK Stock - Real-time Quotes (15min delay)"},
        "fn": ak.stock_hk_spot_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取所有港股的实时行情数据，延迟15分钟更新"
    },
    
    "stock_hk_spot": {
        "label": {"zh_Hans": "新浪-港股-实时行情(延15分钟)", "en_US": "Sina - HK Stock - Real-time Quotes (15min delay)"},
        "fn": ak.stock_hk_spot,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取所有港股的实时行情数据，延迟15分钟更新"
    },
    
    "stock_hk_main_board_spot_em": {
        "label": {"zh_Hans": "东方财富网-港股主板-实时行情(延15分钟)", "en_US": "Eastmoney - HK Main Board - Real-time Quotes (15min delay)"},
        "fn": ak.stock_hk_main_board_spot_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取港股主板的实时行情数据，延迟15分钟更新"
    },
    
    # 新增缺失的接口
    "stock_intraday_em": {
        "label": {"zh_Hans": "东方财富网-最近一个交易日-日内分时数据(包括盘前)-指定股票", "en_US": "Eastmoney - Recent Trading Day - Intraday Data (Including Pre-market) - Specified Stock"},
        "fn": ak.stock_intraday_em,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-最近一个交易日-日内分时数据(包括盘前)-指定股票"
    },
    
    "stock_zh_kcb_daily": {
        "label": {"zh_Hans": "新浪财经-科创板股票历史行情数据-指定股票、复权方式", "en_US": "Sina Finance - STAR Market - Historical Data - Specified Stock and Adjustment"},
        "fn": ak.stock_zh_kcb_daily,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol_with_market_prefix"}},
            "optional": {"adjust": {"type": "str", "default": ""}}
        },
        "supports_timeout": True,
        "description": "新浪财经-科创板股票历史行情数据-指定股票、复权方式"
    },
    
    "stock_zh_growth_comparison_em": {
        "label": {"zh_Hans": "东方财富网-同行比较-成长性比较-指定股票", "en_US": "Eastmoney - Peer Comparison - Growth Comparison - Specified Stock"},
        "fn": ak.stock_zh_growth_comparison_em,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol_with_uppercase_prefix"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-同行比较-成长性比较-指定股票"
    },
    
    "stock_zh_valuation_comparison_em": {
        "label": {"zh_Hans": "东方财富网-同行比较-估值比较-指定股票", "en_US": "Eastmoney - Peer Comparison - Valuation Comparison - Specified Stock"},
        "fn": ak.stock_zh_valuation_comparison_em,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol_with_uppercase_prefix"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-同行比较-估值比较-指定股票"
    },
    
    "stock_zh_dupont_comparison_em": {
        "label": {"zh_Hans": "东方财富网-同行比较-杜邦分析比较-指定股票", "en_US": "Eastmoney - Peer Comparison - DuPont Analysis Comparison - Specified Stock"},
        "fn": ak.stock_zh_dupont_comparison_em,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol_with_uppercase_prefix"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-同行比较-杜邦分析比较-指定股票"
    },
    
    "stock_zh_scale_comparison_em": {
        "label": {"zh_Hans": "东方财富网-同行比较-公司规模-指定股票", "en_US": "Eastmoney - Peer Comparison - Company Scale - Specified Stock"},
        "fn": ak.stock_zh_scale_comparison_em,
        "params": {
            "required": {"symbol": {"type": "str", "preprocess": "normalize_symbol_with_uppercase_prefix"}},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-同行比较-公司规模-指定股票"
    },
    
    "stock_xgsr_ths": {
        "label": {"zh_Hans": "同花顺-新股上市-新股上市首日", "en_US": "THS - New Stock Listing - New Stock First Day"},
        "fn": ak.stock_xgsr_ths,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "同花顺-新股上市-新股上市首日"
    },
    
    "stock_hk_famous_spot_em": {
        "label": {"zh_Hans": "知名港股实时行情数据", "en_US": "Famous HK Stocks Real-time Quotes"},
        "fn": ak.stock_hk_famous_spot_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取知名港股实时行情数据"
    },
    
    "stock_hk_hist": {
        "label": {"zh_Hans": "东方财富网-港股-历史行情数据", "en_US": "Eastmoney - HK Stock - Historical Data"},
        "fn": ak.stock_hk_hist,
        "params": {
            "required": {
                "symbol": {"type": "str"},
                "period": {"type": "str"},
                "start_date": {"type": "str"},
                "end_date": {"type": "str"},
                "adjust": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "获取港股历史行情数据"
    },
    
    "stock_hk_hist_min_em": {
        "label": {"zh_Hans": "东方财富网-港股-每日分时行情", "en_US": "Eastmoney - HK Stock - Daily Minute Data"},
        "fn": ak.stock_hk_hist_min_em,
        "params": {
            "required": {
                "symbol": {"type": "str"},
                "period": {"type": "str"},
                "start_date": {"type": "str"},
                "end_date": {"type": "str"},
                "adjust": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "获取港股每日分时行情数据"
    },
    
    "stock_hk_security_profile_em": {
        "label": {"zh_Hans": "东方财富网-港股-个股-证券资料", "en_US": "Eastmoney - HK Stock - Individual Stock - Security Profile"},
        "fn": ak.stock_hk_security_profile_em,
        "params": {
            "required": {
                "symbol": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "获取港股个股证券资料"
    },
    
    "stock_hk_company_profile_em": {
        "label": {"zh_Hans": "东方财富网-港股-个股-公司资料", "en_US": "Eastmoney - HK Stock - Individual Stock - Company Profile"},
        "fn": ak.stock_hk_company_profile_em,
        "params": {
            "required": {
                "symbol": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "获取港股个股公司资料"
    },
    
    "stock_hk_fhpx_detail_ths": {
        "label": {"zh_Hans": "同花顺-港股-个股-分红派息", "en_US": "THS - HK Stock - Individual Stock - Dividend Distribution"},
        "fn": ak.stock_hk_fhpx_detail_ths,
        "params": {
            "required": {
                "symbol": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "获取港股个股分红派息详情"
    },
    
    "stock_hk_financial_indicator_em": {
        "label": {"zh_Hans": "东方财富网-港股-个股-财务指标-指定股票", "en_US": "East Money - HK Stock - Financial Indicators"},
        "fn": ak.stock_hk_financial_indicator_em,
        "params": {
            "required": {
                "symbol": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-港股-核心必读-最新指标"
    },
    
    "stock_hk_dividend_payout_em": {
        "label": {"zh_Hans": "东方财富网-港股-个股-分红派息-指定股票", "en_US": "East Money - HK Stock - Dividend Payout"},
        "fn": ak.stock_hk_dividend_payout_em,
        "params": {
            "required": {
                "symbol": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-港股-核心必读-分红派息"
    },
    
    "stock_hk_growth_comparison_em": {
        "label": {"zh_Hans": "东方财富网-港股-个股-成长性对比-指定股票", "en_US": "East Money - HK Stock - Growth Comparison"},
        "fn": ak.stock_hk_growth_comparison_em,
        "params": {
            "required": {
                "symbol": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "东方财富网-港股-行业对比-成长性对比"
    },
    
    "stock_hk_daily": {
        "label": {"zh_Hans": "新浪-港股-历史行情数据-指定股票、复权方式", "en_US": "Sina - HK Stock - Historical Data"},
        "fn": ak.stock_hk_daily,
        "params": {
            "required": {
                "symbol": {"type": "str"},
                "adjust": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "新浪-港股-历史行情数据"
    },
    
    "stock_hsgt_fund_flow_summary_em": {
        "label": {"zh_Hans": "东方财富网-沪深港通资金流向", "en_US": "Eastmoney - HSGT Fund Flow Summary"},
        "fn": ak.stock_hsgt_fund_flow_summary_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "获取沪深港通资金流向汇总数据"
    },
    
    "stock_financial_hk_analysis_indicator_em": {
        "label": {"zh_Hans": "港股-财务分析-主要指标", "en_US": "HK - Financial Analysis - Main Indicators"},
        "fn": ak.stock_financial_hk_analysis_indicator_em,
        "params": {
            "required": {
                "symbol": {"type": "str"},
                "indicator": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "获取港股财务分析主要指标"
    },
    
    "stock_financial_hk_report_em": {
        "label": {"zh_Hans": "港股-财务报表-三大报表", "en_US": "HK - Financial Statements - Three Major Reports"},
        "fn": ak.stock_financial_hk_report_em,
        "params": {
            "required": {
                "symbol": {"type": "str"},
                "report_type": {"type": "str"},
                "indicator": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "获取港股财务报表三大报表"
    },
    
    "stock_us_famous_spot_em": {
        "label": {"zh_Hans": "知名美股的实时行情数据", "en_US": "Famous US Stocks Real-time Quotes"},
        "fn": ak.stock_us_famous_spot_em,
        "params": {
            "required": {"category": {"type": "str"}},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取知名美股的实时行情数据"
    },
    
    "stock_financial_us_analysis_indicator_em": {
        "label": {"zh_Hans": "美股-财务分析-主要指标", "en_US": "US - Financial Analysis - Main Indicators"},
        "fn": ak.stock_financial_us_analysis_indicator_em,
        "params": {
            "required": {
                "symbol": {"type": "str"},
                "indicator": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "获取美股财务分析主要指标"
    },
    
    "stock_financial_us_report_em": {
        "label": {"zh_Hans": "美股-财务分析-三大报表", "en_US": "US - Financial Analysis - Three Major Reports"},
        "fn": ak.stock_financial_us_report_em,
        "params": {
            "required": {
                "symbol": {"type": "str"},
                "report_type": {"type": "str"},
                "indicator": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "获取美股财务分析三大报表"
    },
    
    "stock_us_spot_em": {
        "label": {"zh_Hans": "东方财富网-美股-实时行情", "en_US": "Eastmoney - US Stock - Real-time Quotes"},
        "fn": ak.stock_us_spot_em,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取美股实时行情数据"
    },
    
    "stock_us_spot": {
        "label": {"zh_Hans": "新浪-美股-实时行情(延15分钟)", "en_US": "Sina - US Stock - Real-time Quotes (15min delay)"},
        "fn": ak.stock_us_spot,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取美股实时行情数据，延迟15分钟更新"
    },
    
    "stock_us_hist": {
        "label": {"zh_Hans": "东方财富网-美股-每日行情", "en_US": "Eastmoney - US Stock - Daily Data"},
        "fn": ak.stock_us_hist,
        "params": {
            "required": {
                "symbol": {"type": "str"},
                "period": {"type": "str"},
                "start_date": {"type": "str"},
                "end_date": {"type": "str"},
                "adjust": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取美股历史行情数据"
    },
    
    "stock_us_hist_min_em": {
        "label": {"zh_Hans": "东方财富网-美股-每日分时行情(自动最近5天)", "en_US": "Eastmoney - US Stock - Daily Minute Data (Auto 5 Days)"},
        "fn": ak.stock_us_hist_min_em,
        "params": {
            "required": {
                "symbol": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取美股每日分时行情数据，自动返回最近5个交易日"
    },
    
    # 股票技术分析相关接口
    "stock_rank_cxg_ths": {
        "label": {"zh_Hans": "同花顺-技术选股-创新高-指定新高类别", "en_US": "Flush - Technical Stock Selection - Innovation High - Specify High Category"},
        "fn": ak.stock_rank_cxg_ths,
        "params": {
            "required": {
                "symbol": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "同花顺-技术选股-创新高"
    },
    
    "stock_rank_cxd_ths": {
        "label": {"zh_Hans": "同花顺-技术选股-创新低-指定新低类别", "en_US": "Flush - Technical Stock Selection - Innovation Low - Specify Low Category"},
        "fn": ak.stock_rank_cxd_ths,
        "params": {
            "required": {
                "symbol": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "同花顺-技术选股-创新低"
    },
    
    "stock_rank_lxsz_ths": {
        "label": {"zh_Hans": "同花顺-技术选股-连续上涨", "en_US": "Flush - Technical Stock Selection - Continuous Rise"},
        "fn": ak.stock_rank_lxsz_ths,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "同花顺-技术选股-连续上涨"
    },
    
    "stock_rank_lxxd_ths": {
        "label": {"zh_Hans": "同花顺-技术选股-连续下跌", "en_US": "Flush - Technical Stock Selection - Continuous Fall"},
        "fn": ak.stock_rank_lxxd_ths,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "同花顺-技术选股-连续下跌"
    },
    
    "stock_rank_cxfl_ths": {
        "label": {"zh_Hans": "同花顺-技术选股-持续放量", "en_US": "Flush - Technical Stock Selection - Continuous Volume Increase"},
        "fn": ak.stock_rank_cxfl_ths,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "同花顺-技术选股-持续放量"
    },
    
    "stock_rank_cxsl_ths": {
        "label": {"zh_Hans": "同花顺-技术选股-持续缩量", "en_US": "Flush - Technical Stock Selection - Continuous Volume Decrease"},
        "fn": ak.stock_rank_cxsl_ths,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "同花顺-技术选股-持续缩量"
    },
    
    "stock_rank_xstp_ths": {
        "label": {"zh_Hans": "同花顺-技术选股-向上突破-指定均线类型", "en_US": "Flush - Technical Stock Selection - Upward Breakthrough - Specify MA Type"},
        "fn": ak.stock_rank_xstp_ths,
        "params": {
            "required": {
                "symbol": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "同花顺-技术选股-向上突破"
    },
    
    "stock_rank_xxtp_ths": {
        "label": {"zh_Hans": "同花顺-技术选股-向下突破-指定均线类型", "en_US": "Flush - Technical Stock Selection - Downward Breakthrough - Specify MA Type"},
        "fn": ak.stock_rank_xxtp_ths,
        "params": {
            "required": {
                "symbol": {"type": "str"}
            },
            "optional": {}
        },
        "supports_timeout": True,
        "description": "同花顺-技术选股-向下突破"
    },
    
    "stock_rank_ljqs_ths": {
        "label": {"zh_Hans": "同花顺-技术选股-量价齐升", "en_US": "Flush - Technical Stock Selection - Price-Volume Rise"},
        "fn": ak.stock_rank_ljqs_ths,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "同花顺-技术选股-量价齐升"
    },
    
    "stock_rank_ljqd_ths": {
        "label": {"zh_Hans": "同花顺-技术选股-量价齐跌", "en_US": "Flush - Technical Stock Selection - Price-Volume Fall"},
        "fn": ak.stock_rank_ljqd_ths,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "同花顺-技术选股-量价齐跌"
    },
    
    "stock_rank_xzjp_ths": {
        "label": {"zh_Hans": "同花顺-技术选股-险资举牌", "en_US": "Flush - Technical Stock Selection - Insurance Capital Disclosure"},
        "fn": ak.stock_rank_xzjp_ths,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "同花顺-技术选股-险资举牌"
    },
    
    "stock_esg_msci_sina": {
        "label": {"zh_Hans": "新浪财经-ESG评级-MSCI", "en_US": "Sina Finance - ESG Rating - MSCI"},
        "fn": ak.stock_esg_msci_sina,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "新浪财经-ESG评级-MSCI"
    },
    
    "stock_esg_rft_sina": {
        "label": {"zh_Hans": "新浪财经-ESG评级-路孚特", "en_US": "Sina Finance - ESG Rating - Refinitiv"},
        "fn": ak.stock_esg_rft_sina,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": True,
        "description": "新浪财经-ESG评级-路孚特"
    },
    
    # 个股综合技术指标工具（计算工具）
    "stock_comprehensive_technical_indicators": {
        "label": {"zh_Hans": "个股综合技术指标(拓展指标)", "en_US": "Stock Comprehensive Technical Indicators (Extended Indicators)"},
        "fn": None,  # 这是计算工具，不直接调用AKShare接口
        "params": {
            "required": {
                "symbol": {"type": "str"},
                "indicator": {"type": "str"}
            },
            "optional": {
                "period_daily": {"type": "str"},
                "period_minute": {"type": "str"},
                "start_date": {"type": "str"},
                "end_date": {"type": "str"},
                "adjust": {"type": "str"},
                "retries": {"type": "int"},
                "timeout": {"type": "float"}
            }
        },
        "supports_timeout": True,
        "description": "根据个股的原始接口数据，计算个股综合性或拓展性指标，以更深层次地反映个股的整体情况，如，基于历史数据的趋势动量震荡指标和基于最新财务数据的动态估值指标"
    },
    
    "stock_us_spot": {
        "label": {"zh_Hans": "新浪-美股-实时行情(延15分钟)", "en_US": "Sina - US Stock - Real-time Quotes (15min delay)"},
        "fn": ak.stock_us_spot,
        "params": {
            "required": {},
            "optional": {}
        },
        "supports_timeout": False,
        "description": "获取美股实时行情数据，延迟15分钟更新"
    }
}


def get_interface_config(interface_name: str) -> Optional[Dict[str, Any]]:
    """获取接口配置"""
    return REGISTRY.get(interface_name)


def get_available_interfaces() -> List[str]:
    """获取所有可用的接口名称"""
    return list(REGISTRY.keys())


def validate_interface_params(interface_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """验证并处理接口参数"""
    import logging
    logging.info(f"validate_interface_params called with interface: {interface_name}, params: {params}")
    
    config = get_interface_config(interface_name)
    if not config:
        raise ValueError(f"Unknown interface: {interface_name}")
    
    processed_params = {}
    
    # 只处理接口配置中定义的参数，忽略其他参数
    all_defined_params = set(config["params"]["required"].keys()) | set(config["params"]["optional"].keys())
    
    # 处理必需参数
    for param_name, param_config in config["params"]["required"].items():
        if param_name not in params:
            if "default" in param_config:
                processed_params[param_name] = param_config["default"]
            else:
                raise ValueError(f"Required parameter '{param_name}' is missing")
        else:
            value = params[param_name]
            # 类型转换
            if param_config["type"] == "str":
                value = str(value)
            elif param_config["type"] == "int":
                value = int(value)
            elif param_config["type"] == "float":
                value = float(value)
            
            # 参数验证
            if param_name == "period" and interface_name == "stock_zh_a_hist":
                # stock_zh_a_hist 的 period 参数只接受 daily, weekly, monthly
                valid_periods = ["daily", "weekly", "monthly"]
                if value not in valid_periods:
                    logging.warning(f"Invalid period '{value}' for stock_zh_a_hist, using default 'daily'")
                    value = "daily"
            
            # 日期验证
            if param_name in ["start_date", "end_date", "date"]:
                try:
                    from datetime import datetime
                    # 解析日期字符串 (格式: YYYYMMDD)
                    if len(str(value)) == 8:
                        date_obj = datetime.strptime(str(value), "%Y%m%d")
                        today = datetime.now()
                        # 检查是否是未来日期（超过今天）
                        if date_obj.date() > today.date():
                            logging.warning(f"Future date '{value}' detected for {param_name}, using current date")
                            value = today.strftime("%Y%m%d")
                except ValueError:
                    logging.warning(f"Invalid date format '{value}' for {param_name}")
                    # 保持原值，让AKShare函数处理
            
            # 预处理
            if "preprocess" in param_config:
                preprocess_func = param_config["preprocess"]
                if preprocess_func == "normalize_symbol":
                    # 只对 symbol 参数应用 normalize_symbol
                    if param_name == "symbol":
                        value = normalize_symbol(value)
                    else:
                        # 对于非 symbol 参数，直接使用原值
                        pass
                elif preprocess_func == "normalize_symbol_with_market_prefix":
                    # 只对 symbol 参数应用 normalize_symbol_with_market_prefix
                    if param_name == "symbol":
                        value = normalize_symbol_with_market_prefix(value)
                    else:
                        # 对于非 symbol 参数，直接使用原值
                        pass
                elif preprocess_func == "normalize_symbol_with_uppercase_prefix":
                    # 只对 symbol 参数应用 normalize_symbol_with_uppercase_prefix
                    if param_name == "symbol":
                        value = normalize_symbol_with_uppercase_prefix(value)
                    else:
                        # 对于非 symbol 参数，直接使用原值
                        pass
                elif preprocess_func == "normalize_symbol_with_dot":
                    # 只对 symbol 参数应用 normalize_symbol_with_dot
                    if param_name == "symbol":
                        value = normalize_symbol_with_dot(value)
                    else:
                        # 对于非 symbol 参数，直接使用原值
                        pass
                elif preprocess_func == "normalize_us_symbol":
                    # 对美股股票代码进行标准化
                    if param_name == "symbol":
                        value = normalize_us_symbol(value)
                    else:
                        # 对于非 symbol 参数，直接使用原值
                        pass
                elif preprocess_func == "get_symbol_candidates":
                    # 对于需要多候选的接口，返回候选列表
                    return get_symbol_candidates(value)
            
            processed_params[param_name] = value
    
    # 处理可选参数
    for param_name, param_config in config["params"]["optional"].items():
        if param_name in params:
            value = params[param_name]
            if param_config["type"] == "str":
                value = str(value)
            elif param_config["type"] == "int":
                value = int(value)
            elif param_config["type"] == "float":
                value = float(value)
            processed_params[param_name] = value
        elif "default" in param_config:
            processed_params[param_name] = param_config["default"]
    
    logging.info(f"validate_interface_params returning: {processed_params}")
    return processed_params

