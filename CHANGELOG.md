# Changelog

All notable changes to the AKShare Stock Data Plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.7.0] - 2025-01-XX

### Release Summary
- 🎉 **工具重构优化**: v0.7.0 版本，工具结构优化和接口标准化
- 🔧 **工具合并**: 合并同花顺和东方财富板块接口为独立工具
- 📝 **接口标准化**: 统一接口命名规范，提升用户体验
- 🧹 **代码优化**: 清理旧工具，优化工具结构

### Added
- **新增工具**: `get_board_ths` - 获取同花顺板块数据
  - 合并了 `get_concept_board` 和 `get_industry_board` 中的5个同花顺接口
  - 包括：概念板块名列表、概念板块指数、概念板块简介、行业一览表、行业板块指数
- **新增工具**: `get_board_em` - 获取东方财富板块数据
  - 合并了 `get_concept_board` 和 `get_industry_board` 中的10个东方财富接口
  - 包括：概念板块和行业板块的列表、实时行情、板块成份、历史行情、分时数据

### Changed
- **工具重构**: 将板块相关工具拆分为更细粒度的工具
  - `get_concept_board` 和 `get_industry_board` 已移除
  - 新增 `get_board_ths` 和 `get_board_em` 替代
- **接口标准化**: 统一接口命名规范
  - `get_stock_hot` 工具接口命名标准化
  - `get_limit_up_down` 工具接口命名标准化
- **版本更新**: 插件版本升级到 v0.7.0

### Removed
- **移除工具**: `get_concept_board` - 已拆分为 `get_board_ths` 和 `get_board_em`
- **移除工具**: `get_industry_board` - 已拆分为 `get_board_ths` 和 `get_board_em`

### Technical
- 基于 AKShare 1.16.92+ 版本
- Python 3.12+ 支持
- Dify Plugin SDK 0.2.1+
- 完整的错误处理和参数验证机制

### Documentation
- 更新版本号到 v0.7.0
- 更新工具文档和示例

---

## [0.6.0] - 2025-10-28

### Release Summary
- 🎉 **稳定版本发布**: v0.6.0 正式版，完成11个专业工具的开发和测试
- 📦 **Marketplace就绪**: 准备发布到Dify Marketplace
- 🧹 **代码清理**: 清除所有临时文件、缓存和日志，保留核心代码和文档
- 🎨 **图标升级**: 设计并替换新插件图标，提升视觉专业性

### Added
- 完成11个专业工具的完整实现
  - stock_market_summary（股票市场总貌）
  - stock_individual_info_summary（个股信息总貌）
  - stock_spot_quotations（实时行情数据）
  - stock_hist_quotations（历史行情数据）
  - stock_financial_analysis（股票财务数据分析）
  - stock_fund_flow_analysis（资金流向分析）
  - stock_technical_analysis（股票技术分析）
  - stock_comprehensive_technical_indicators（个股综合技术指标）
  - stock_hk_data（港股数据）
  - stock_us_data（美股数据）
  - stock_hsgt_holdings（沪深港通持股）
  - stock_index_data（股票指数数据）

### Changed
- 项目结构清理和优化
- 文档完善和更新
- 版本管理标准化

### Fixed
- 清除所有Python缓存文件（__pycache__）
- 删除临时开发文档和日志文件
- 移除旧版本的打包文件

### Technical
- 基于 AKShare 1.16.92+ 版本
- Python 3.12+ 支持
- Dify Plugin SDK 0.2.1+
- 完整的错误处理和参数验证机制

### Documentation
- 保留完整的中英文文档
- 保留AKShare接口参考规范
- 保留应用示例和开发实践文档

---

## [0.5.1] - 2025-01-15

### Compatibility
- ✅ **完全向后兼容**: 与版本0.5.0完全兼容，所有基于0.5.0版本的工作流可直接使用
- ✅ **零修改升级**: 现有Dify工作流无需任何调整即可使用新版本
- ✅ **工具顺序保持**: 保持0.5.0版本的工具顺序，确保工作流识别正确

### Added
- **个股综合技术指标工具** (`stock_comprehensive_technical_indicators`): 新增基于个股历史数据计算多种技术指标的综合分析工具
  - 支持5种指标类型：趋势动量震荡指标(日频)、趋势动量震荡指标(分钟)、动态估值指标、历史估值指标、个股基本信息汇总
  - 技术指标支持：移动平均线(MA5/10/20/30/60)、RSI(6/12/24)、MACD、KDJ、布林带、成交量均线(VMA5/10/20)
  - 复权方式支持：前复权(qfq)、后复权(hfq)、不复权三种复权方式
  - 多格式输出：支持MARKDOWN和JSON两种格式的技术指标数据输出
- **美股工具参数分离**: 将美股工具的symbol参数分离为独立的symbol(股票代码)和category(类别)参数
  - symbol参数：用于个股数据查询，支持AAPL、MSFT等格式
  - category参数：用于知名股票分类查询，支持科技类、金融类等10个行业类别
- **美股财务分析接口修复**: 修复美股财务分析接口，使用通用的`ak.stock_financial_analysis_indicator`接口
- **沪深港通资金流向接口迁移**: 将`stock_hsgt_fund_flow_summary_em`接口从港股工具迁移到沪深港通工具

### Changed
- **美股工具参数优化**: 重新整理美股工具参数排序，按逻辑分组显示
  - 核心参数：接口选择
  - 股票标识参数：symbol(股票代码)、category(类别)
  - 时间周期参数：period(历史行情)、period2(分时行情)
  - 日期范围参数：start_date、end_date
  - 数据调整参数：adjust
  - 财务分析参数：indicator_us、report_type
  - 系统配置参数：retries、timeout
- **技术指标计算统一化**: 统一技术指标参数，无论什么时间周期都使用相同的标准参数
- **输出格式优化**: 优化Markdown表格格式，确保与Markdown转XLSX节点兼容
- **错误处理增强**: 改进错误提示信息，提供更具体的建议和解决方案

### Fixed
- **美股代码格式转换**: 修复美股历史数据接口的代码格式转换问题，自动添加105.前缀
- **美股财务分析接口**: 修复`stock_financial_us_analysis_indicator_em`接口的NoneType错误
- **参数验证逻辑**: 修复参数验证中的逻辑问题，确保参数正确传递
- **代码结构优化**: 修复代码中的缩进错误和语法问题

### Dependencies
- **技术指标计算优化**: 使用pandas内置函数实现技术指标计算
  - 移除TA-Lib和pandas-ta依赖，确保广泛兼容性
  - 使用pandas向量化计算，性能更优
  - 支持所有Dify部署环境，无需编译环境
- 更新: akshare>=1.16.92 (股票数据接口库)
- 自动安装: pandas和numpy由akshare自动安装，无需显式声明

### Technical
- 优化技术指标计算性能和准确性
- 增强错误处理和参数验证
- 基于AKShare历史数据接口进行技术指标计算
- 实现模块化的技术指标计算架构
- 支持多种技术分析库的自动切换

---

## [0.5.0] - 2025-09-18

### Added
- **113个数据接口**: 从103个接口扩展到113个接口，新增10个数据接口
- **服务对象说明**: 添加了针对学术研究人员和AI应用开发者的服务对象描述
- **巨潮资讯接口优化**: 更新了巨潮资讯接口的标签和描述信息
- **财务分析参数重构**: 将indicator参数拆分为indicator_ths、indicator_hk、indicator_us三个独立参数

### Changed
- **接口数量更新**: 所有文档中的接口数量从103个更新为113个
- **参数描述优化**: 财务分析工具的参数描述更加清晰和具体
- **文档结构改进**: 简化了服务对象部分，突出核心用户群体
- **编码兼容性**: 改进了Windows环境下的Unicode编码处理

### Fixed
- **Unicode编码问题**: 解决了Windows环境下GBK编码导致的UnicodeEncodeError
- **跨平台兼容性**: 确保插件在Windows、Linux、macOS上的稳定运行
- **参数验证**: 修复了财务分析工具中参数验证的逻辑问题

### Removed
- **乐咕乐股接口**: 移除了5个乐咕乐股相关接口（stock_a_indicator_lg等）

---

## [Unreleased]

### Added
- Comprehensive parameter validation with detailed format descriptions
- Multi-language support for all parameter descriptions
- Enhanced error handling with specific suggestions
- GitHub repository structure with proper documentation
- **Legal compliance documentation (LEGAL.md)**
- **Enhanced acknowledgments and AKShare attribution**
- **Open source compliance notices**

### Changed
- Improved parameter descriptions with examples and format requirements
- Updated interface labels to match AKShare documentation exactly
- Enhanced README.md with installation and usage instructions
- **Updated all descriptions to clearly indicate AKShare wrapper nature**
- **Added proper attribution to AKShare, FuShare, and TuShare projects**

### Fixed
- Corrected interface display names for US and HK stock data
- Fixed parameter validation for date formats and stock codes
- Improved error messages for better user experience

### Legal & Compliance
- Added comprehensive legal disclaimers
- Enhanced privacy policy with AKShare dependency information
- Added proper open source compliance notices
- Included financial data usage disclaimers
- Added academic research purpose clarifications

## [0.0.2] - 2025-01-03

### Added
- 15 comprehensive stock data interfaces
- Multi-language support (English, Chinese, Portuguese, Traditional Chinese)
- Robust error handling with retry mechanisms
- Parameter validation and preprocessing
- Support for A-shares, B-shares, US stocks, HK stocks, and STAR market data

### Features
- **A-Share Data**: Daily frequency data, pre-market data, risk warning board, new stocks, delisted stocks
- **B-Share Data**: Real-time B-share data
- **US Stock Data**: Real-time, daily, and minute data
- **Hong Kong Stock Data**: Minute-level data
- **Other Data**: Individual stock info, quotes, company news, STAR board reports, A/H share comparison

### Technical
- Built on AKShare library for reliable data access
- No token required for data access
- Markdown and JSON output formats
- Configurable retry and timeout parameters
- Memory-efficient processing

## [0.0.1] - 2025-01-01

### Added
- Initial release
- Basic plugin structure
- Core AKShare integration
- Basic error handling
- Simple parameter validation

---

## Version History

- **0.0.1**: Initial release with basic functionality
- **0.0.2**: Enhanced with comprehensive interfaces and multi-language support
- **0.5.0**: Major update with 113 interfaces, improved encoding, and parameter refactoring
- **Unreleased**: Improved documentation and GitHub repository structure
