# AKShare 股票数据插件 for Dify

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Dify Plugin](https://img.shields.io/badge/Dify-Plugin-green.svg)](https://dify.ai/)
[![AKShare](https://img.shields.io/badge/AKShare-Latest-blue.svg)](https://github.com/akfamily/akshare)
[![Download Plugin](https://img.shields.io/badge/Download-Plugin%20Package-blue)](https://github.com/shaoxing-xie/akshare-stockdata-plugin/releases/tag/v0.6.0)
[![接口数量](https://img.shields.io/badge/接口数量-139-blue.svg)](https://github.com/shaoxing-xie/akshare-stockdata-plugin/blob/main/AKShare%20股票数据插件详细功能文档.md)
[![详细文档](https://img.shields.io/badge/详细文档-查看-green.svg)](https://github.com/shaoxing-xie/akshare-stockdata-plugin/blob/main/AKShare%20股票数据插件详细功能文档.md)

## 📥 快速下载

[![Download Plugin](https://img.shields.io/badge/Download-Plugin%20Package-blue)](https://github.com/shaoxing-xie/akshare-stockdata-plugin/releases/tag/v0.6.0)

**直接下载最新版本插件包** | [查看所有版本](https://github.com/shaoxing-xie/akshare-stockdata-plugin/releases)

## 📞 联系方式

- **作者**: shaoxing-xie
- **邮箱**: sxxiefg@163.com
- **代码库**: [https://github.com/shaoxing-xie/akshare-stockdata-plugin](https://github.com/shaoxing-xie/akshare-stockdata-plugin)
- **问题反馈**: [GitHub Issues](https://github.com/shaoxing-xie/akshare-stockdata-plugin/issues)

## 📋 概述

**AKShare 股票数据插件** 是一个专为 Dify 平台开发的综合性股票数据工具，基于知名的 [AKShare](https://github.com/akfamily/akshare) Python 库构建。本插件为用户提供了一站式的股票市场数据访问解决方案，涵盖实时行情、历史数据、财务分析、资金流向、技术分析、沪深港通等多个维度的专业股票信息。
> **功能亮点**: 提供139个数据接口，覆盖全球股票市场。查看 [完整功能文档](https://github.com/shaoxing-xie/akshare-stockdata-plugin/blob/main/AKShare%20股票数据插件详细功能文档.md) 获取所有接口详情、参数指南和技术参考。

> **重要声明**: 本插件是 AKShare 库的 Dify 平台集成工具，AKShare 是一个专为学术研究目的设计的开源金融数据接口库。我们对 AKShare 项目团队的卓越工作表示诚挚感谢。

> **⚠️ 接口更新说明**: 由于网络传输稳定性问题，已移除以下8个股东分析接口：
> - `stock_gdfx_free_holding_analyse_em` - 股东持股分析(十大流通股东)
> - `stock_gdfx_holding_analyse_em` - 股东持股分析(十大股东)
> - `stock_gdfx_free_holding_detail_em` - 股东持股明细(十大流通股东)
> - `stock_gdfx_holding_detail_em` - 股东持股明细(十大股东)
> - `stock_gdfx_free_holding_statistics_em` - 股东持股统计(十大股东)
> - `stock_gdfx_holding_statistics_em` - 股东持股统计(十大股东)
> - `stock_gdfx_free_holding_change_em` - 股东持股变动统计(十大流通股东)
> - `stock_gdfx_holding_change_em` - 股东持股变动统计(十大股东)
> 
> 其他股东相关接口（十大股东等）仍然正常可用。

## 🚀 核心特点

### 💎 **无需API密钥**
- ✅ **零配置使用**: 无需申请任何API密钥或令牌
- ✅ **即插即用**: 安装后立即可用，无需复杂配置
- ✅ **成本节约**: 完全免费使用，无使用次数限制

### 🔧 **版本兼容性**
- ✅ **Dify 0.3.0+**: 完全兼容最新版本Dify
- ✅ **依赖管理**: 使用requirements.txt确保稳定安装
- ✅ **自动依赖**: AKShare自动安装pandas和numpy，无需手动配置

### 🌐 **权威数据源**
- 📊 **东方财富网**: 实时行情、财务数据、市场分析
- 📈 **新浪财经**: 历史行情、股票资讯
- 🏢 **同花顺**: 技术指标、资金流向分析
- 💰 **腾讯财经**: 港股、美股数据
- 📱 **网易财经**: 市场概况、个股信息
- 🔗 **公开API**: 证券交易所官方数据接口

### 🛠️ **强大功能矩阵**
- 🎯 **11个专业工具**: 覆盖股票数据分析的各个方面
  - **10个原始接口工具**: 基于AKShare的原始数据接口
  - **1个扩展指标工具**: 专业的技术指标计算和分析
- 🌍 **139个数据接口**: 广泛覆盖全球主要股票市场
- 📊 **多市场支持**: A股、B股、港股、美股、科创板、北交所
- 🔄 **实时+历史**: 既有实时行情，也有历史数据分析
- 📋 **双重输出**: Markdown表格 + JSON格式，便于阅读和处理
- 📈 **技术分析**: 专业的技术指标计算和分析工具

### 🔧 **技术优势**
- 🛡️ **智能错误处理**: 自动重试机制，优雅的错误恢复
- 🌐 **完整Unicode支持**: 完美处理中文字符和特殊符号
- ⚡ **性能优化**: 子进程隔离，高效内存管理
- 🔄 **参数验证**: 自动参数校验和格式转换

## 👥 服务对象

### 🎓 **学术研究人员**
- 金融学研究者进行市场分析和学术研究
- 经济学学者研究股市波动规律
- 数据科学研究者进行量化分析

### 🤖 **AI应用开发者**
- 构建智能投资助手和财经聊天机器人
- 开发股票分析和预测模型
- 创建自动化投资决策系统


## 📦 如何安装

### 方式一：直接下载安装（推荐）

[![Download Plugin](https://img.shields.io/badge/Download-Plugin%20Package-blue)](https://github.com/shaoxing-xie/akshare-stockdata-plugin/raw/main/releases/AKShare-Stockdata-plugin-v0.5.0.difypkg)

1. **快速下载**：点击上方按钮直接下载最新版本插件包
2. **在Dify中安装**：
   - 打开您的 Dify 工作空间
   - 导航至 **工具** → **插件** → **安装插件**
   - 选择 **"从文件安装"**
   - 上传下载的 `.difypkg` 文件
   - 点击 **安装** 按钮

### 方式二：从releases目录下载
1. 访问 [releases目录](https://github.com/shaoxing-xie/akshare-stockdata-plugin/tree/main/releases)
2. 下载 **"AKShare-Stockdata-plugin-v0.5.1.difypkg"** 文件
3. 按照方式一的步骤在Dify中安装

### 方式三：通过GitHub Releases
1. 访问 [GitHub Releases](https://github.com/shaoxing-xie/akshare-stockdata-plugin/releases)
2. 下载最新版本的插件包
3. 按照方式一的步骤在Dify中安装

### 方式三：手动安装
1. 克隆本仓库到本地
   ```bash
   git clone https://github.com/shaoxing-xie/akshare-stockdata-plugin.git
   ```
2. 安装Python依赖
   ```bash
   cd akshare-stockdata-plugin
   pip install -r requirements.txt
   ```
3. 使用 Dify CLI 打包插件
   ```bash
   dify plugin package
   ```
4. 在 Dify 中上传生成的 .difypkg 文件

安装后，参考 [详细功能文档](https://github.com/shaoxing-xie/akshare-stockdata-plugin/blob/main/AKShare%20股票数据插件详细功能文档.md) 快速了解所有接口。

## 🎯 如何使用

### 快速上手三步骤
1. **选择工具**: 从11个专业工具中选择适合的工具
2. **选择接口**: 从113个数据接口中选择具体的数据源
3. **设置参数**: 配置股票代码、日期范围等参数

### 使用示例

#### 获取股票历史行情
```json
{
  "interface": "东方财富网-A股历史行情数据",
  "symbol": "600519",
  "period": "daily",
  "start_date": "20240101",
  "end_date": "20241231",
  "adjust": "qfq"
}
```

#### 获取实时行情数据
```json
{
  "interface": "东方财富网-沪A股票实时行情",
  "symbol": "600519"
}
```

#### 查询个股财务数据
```json
{
  "interface": "东方财富网-业绩快报-资产负债表",
  "date": "20240331"
}
```

更多示例见 [详细功能文档](https://github.com/shaoxing-xie/akshare-stockdata-plugin/blob/main/AKShare%20股票数据插件详细功能文档.md)。

## 🎨 应用示例展示

### 📊 个股诊断报告示例

我们基于插件构建了一个完整的个股诊断工作流，可以自动生成专业的个股诊断报告：

<img src="_assets/result.png" alt="个股诊断报告示例" width="800"/>

### 🔄 工作流配置

以下是个股诊断助手的工作流配置，展示了如何组合使用多个工具来实现复杂的股票分析：

<img src="_assets/workflow.png" alt="个股诊断助手工作流" width="800"/>

## 🛠️ 工具详情

### 🏠 **工具一：股票市场总貌**
- **接口数量**: 20个
- **功能**: 获取整体市场概况和统计数据，包括上交所、深交所市场总貌、股权质押、商誉数据、股票账户统计、千股千评、新股申购收益率、停复牌提醒、分红派息等
- **适用场景**: 市场分析、宏观研究、风险监控

### 📊 **工具二：股票实时行情**  
- **接口数量**: 11个
- **功能**: 获取各市场实时股票行情数据，包括沪深京A股实时行情，新股数据，AH股比价，AB股比价，次新股数据，两网及退市股票等
- **适用场景**: 实时监控、交易决策、跨市场比较

### 📈 **工具三：股票历史行情**
- **接口数量**: 5个  
- **功能**: 获取历史价格数据，包括A股日线和分时数据，科创板历史数据，盘前数据等
- **适用场景**: 技术分析、回测研究、量化建模

### 🏢 **工具四：个股信息总貌**
- **接口数量**: 32个
- **功能**: 获取个股基本信息、财务数据、研究报告，包括A股的股票信息、行情报价、主营业务、新闻资讯、分红配股、资产负债表、股东持股分析等
- **适用场景**: 基本面分析、投资研究、价值评估、股东结构分析

### 💰 **工具五：股票财务数据分析**
- **接口数量**: 10个
- **功能**: 获取财务报表和业绩数据，包括A股业绩快报（利润表、现金流量表、资产负债表）、同花顺财务指标、新浪财经财务指标等
- **适用场景**: 财务分析、价值投资、跨市场比较

### 🌊 **工具六：资金流向分析**
- **接口数量**: 11个
- **功能**: 分析资金流向和市场情绪，包括个股资金流向、板块资金流向排行、主力资金流向、行业和概念历史资金流向、筹码分布等
- **适用场景**: 资金面分析、市场情绪判断、主力动向追踪

### 📊 **工具七：股票技术分析**
- **接口数量**: 18个
- **功能**: 技术指标和创新高低数据，包括创新高低、连续上涨下跌、持续放量缩量、均线突破、量价分析、ESG评级、个股指标、股息率等
- **适用场景**: 技术分析、趋势判断、ESG投资、股息投资

### 🌉 **工具八：沪深港通持股**
- **接口数量**: 8个
- **功能**: 北向资金持股和流向数据，包括港股通成份股、沪深港通分时数据、板块排行、个股排行、实时行情、历史数据、具体股票持股、沪深港通资金流向等
- **适用场景**: 外资动向分析、市场情绪、北向资金追踪

### 🇭🇰 **工具九：港股数据** ⭐ **独立工具**
- **接口数量**: 11个
- **功能**: 港股相关的数据接口，包括港股实时行情、历史数据、财务分析、公司资料、分红派息等
- **适用场景**: 港股投资分析、跨市场比较

### 🇺🇸 **工具十：美股数据** ⭐ **独立工具**
- **接口数量**: 8个
- **功能**: 美股相关的数据接口，包括美股实时行情、历史数据、财务分析、知名股票分类等
- **适用场景**: 美股投资分析、全球市场研究

### 📈 **工具十一：个股综合技术指标** ⭐ **扩展指标工具**
- **接口数量**: 5个
- **功能**: 基于个股历史数据计算多种技术指标的综合分析工具，支持5种指标类型
  - 趋势动量震荡指标(日频)：MA5/10/20/30/60、RSI6/12/24、MACD、KDJ、布林带、VMA5/10/20
  - 趋势动量震荡指标(分钟)：基于分钟级K线数据计算MA5/10/20/30/60、RSI6/12/24、MACD、KDJ、布林带、VMA5/10/20等技术指标
  - 动态估值指标：PE、PB、PCF、PEG、财务评分等估值指标
  - 历史估值指标：历史PE/PB/PCF/PEG等估值时间序列
  - 个股基本信息汇总：证券资料、公司概况、业务范围等基本信息
- **适用场景**: 技术分析、量化研究、投资决策、学术研究

## 🔒 隐私与安全

本插件严格遵循数据隐私保护原则：
- ✅ **不存储用户数据**: 所有数据仅在内存中处理，不进行持久化存储
- ✅ **不收集个人信息**: 不获取或传输任何用户个人敏感信息  
- ✅ **透明数据处理**: 所有数据来源和处理过程完全透明
- ✅ **开源可审计**: 源代码完全开放，可供审查和验证

详细信息请参阅 [隐私政策](PRIVACY.md)

结合 [详细功能文档](https://github.com/shaoxing-xie/akshare-stockdata-plugin/blob/main/AKShare%20股票数据插件详细功能文档.md)，了解数据处理细节。

## ⚖️ 合规声明

本插件完全符合相关法律法规要求：
- 📋 **开源合规**: 基于MIT许可证的开源项目
- 🌐 **数据合规**: 仅使用公开可访问的数据源
- 🔍 **透明运营**: 数据获取方式和处理流程完全透明
- ⚖️ **法律合规**: 严格遵守相关金融数据使用法规

详细信息请参阅 [法律声明](LEGAL.md)

## 🙏 致谢

### AKShare 项目团队
本插件基于优秀的 [AKShare](https://github.com/akfamily/akshare) 库构建，我们向以下项目表示诚挚感谢：
- **AKShare 开发团队**: 创建和维护这个综合性的金融数据接口库
- **开源社区贡献者**: 为项目发展做出的宝贵贡献

### Dify 平台
感谢 [Dify](https://dify.ai/) 团队提供了优秀的AI应用开发平台，让金融数据的AI应用变得更加便捷。

## 📄 许可证

本项目采用 **MIT 许可证** - 详情请参阅 [LICENSE](LICENSE) 文件。

**注意**: 本插件是 AKShare 库的封装工具。底层数据访问功能请参考 AKShare 的 MIT 许可证条款。

## 🤝 贡献指南

我们欢迎社区贡献！请按以下步骤参与：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📞 技术支持

如果您遇到问题或有建议：
1. 查看 [Issues](https://github.com/shaoxing-xie/akshare-stockdata-plugin/issues) 页面
2. 创建包含详细信息的新 issue
3. 参考 AKShare 官方文档

## 🔄 版本升级

### 从0.5.0升级到0.5.1
- ✅ **完全向后兼容**：所有基于0.5.0版本的工作流可直接使用，无需修改
- ✅ **零修改升级**：现有Dify工作流无需任何调整
- ✅ **功能增强**：获得更多数据接口和功能

👉 **[详细升级指南](UPGRADE_GUIDE.md)** - 完整的版本升级说明

## 📚 详细功能文档

插件提供11个专业工具共139个数据接口的完整功能。为了保持README的简洁性，详细的接口文档已独立为专门的技术文档：

### 📖 **完整技术文档**
👉 **[AKShare 股票数据插件详细功能文档.md](https://github.com/shaoxing-xie/akshare-stockdata-plugin/blob/main/AKShare%20股票数据插件详细功能文档.md)** - 您的接口宝典！

该文档包含：
- ✅ **113个接口的完整说明** - 每个接口的功能、参数、AKShare引用信息
- ✅ **11个工具的详细分类** - 按工具分类的完整接口列表  
- ✅ **参数使用指南** - 详细的参数输入说明和格式要求
- ✅ **技术参考信息** - 完整的AKShare接口引用和目标地址

### 🎯 **快速导航**
- [工具1：股票市场总貌 (20个接口)](AKShare%20股票数据插件详细功能文档.md#工具1股票市场总貌-stock-market-summary)
- [工具2：股票实时行情 (11个接口)](AKShare%20股票数据插件详细功能文档.md#工具2股票实时行情-stock-spot-quotations)  
- [工具3：股票历史行情 (5个接口)](AKShare%20股票数据插件详细功能文档.md#工具3股票历史行情-stock-historical-quotations)
- [工具4：个股信息总貌 (32个接口)](AKShare%20股票数据插件详细功能文档.md#工具4个股信息总貌-individual-stock-info-summary)
- [工具5：股票财务数据分析 (10个接口)](AKShare%20股票数据插件详细功能文档.md#工具5股票财务数据分析-stock-financial-data-analysis)
- [工具6：资金流向分析 (11个接口)](AKShare%20股票数据插件详细功能文档.md#工具6资金流向分析-capital-flow-analysis)
- [工具7：股票技术分析 (18个接口)](AKShare%20股票数据插件详细功能文档.md#工具7股票技术分析-stock-technical-analysis)
- [工具8：沪深港通持股 (8个接口)](AKShare%20股票数据插件详细功能文档.md#工具8沪深港通持股-hsgt-holdings)
- [工具9：港股数据 (11个接口)](AKShare%20股票数据插件详细功能文档.md#工具9港股数据-stock-hk-data) ⭐ **独立工具**
- [工具10：美股数据 (8个接口)](AKShare%20股票数据插件详细功能文档.md#工具10美股数据-stock-us-data) ⭐ **独立工具**
- [工具11：个股综合技术指标 (5个接口)](AKShare%20股票数据插件详细功能文档.md#工具11个股综合技术指标-stock-comprehensive-technical-indicators) ⭐ **扩展指标工具**

---

## 🔧 故障排除

### ❌ **常见问题解决**

#### 1. **插件安装失败 - 依赖问题**
**症状**: 插件安装时出现依赖相关错误

**解决方案**:
```bash
# 方法1: 重新安装插件
# 在Dify中重新安装插件，系统会自动处理依赖

# 方法2: 检查网络连接
# 确保网络连接正常，能够访问PyPI
```

#### 2. **工具调用返回空数据**
**症状**: 工具调用成功但返回 `{"data": []}`

**可能原因**:
- 网络连接问题
- 数据源暂时不可用
- 参数配置错误

**解决方案**:
- 检查网络连接
- 增加重试次数和超时时间
- 验证参数格式（日期格式：YYYYMMDD）

#### 3. **Dify 0.3.0+ 兼容性问题**
**症状**: 在新版本Dify中插件无法正常工作

**解决方案**:
- 确保使用最新版本插件包
- 检查 `.env` 文件配置：
  ```env
  FORCE_VERIFYING_SIGNATURE=false
  PLUGIN_PYTHON_ENV_INIT_TIMEOUT=600
  ```

#### 4. **插件安装后Dify工具中没有显示插件**
**症状**: 插件安装后，在Dify的工具列表中看不到插件

**可能原因和解决方案**:

**情况一：预编译尚未完成**
- ⏰ **检查预编译状态**: 查看Dify后台插件运行日志，确认预编译是否还在进行中
- 📊 **监控进度**: 预编译过程通常需要5-15分钟，请耐心等待
- 🔍 **查看日志**: 在Dify管理后台查看插件运行日志，确认编译进度

**情况二：预编译已完成但工具未显示**
- 🔄 **重新安装**: 预编译完成后，如果Dify工具中还没有显示插件，请再次安装一次插件包，插件就会正常显示
- ✅ **正常现象**: 这是Dify插件系统的已知问题，重新安装即可解决

**技术说明**:
- 预编译超时设置：30分钟（足够完成编译）
- 已优化`.difyignore`文件，排除测试文件以加快编译速度
- 这是Dify插件系统的通用问题，所有插件都可能遇到

### 🔍 **兼容性检查**

运行内置的兼容性检查脚本：
```bash
python compatibility_check.py
```

### 📞 **获取帮助**

如果问题仍然存在，请：
1. 查看 [GitHub Issues](https://github.com/shaoxing-xie/akshare-stockdata-plugin/issues)
2. 发送邮件至: sxxiefg@163.com
3. 提供详细的错误日志和Dify版本信息

## 🔗 相关文档

- 📋 **[主要功能介绍](README.md)** - 插件概述和快速入门
- 📚 **[详细功能文档](AKShare%20股票数据插件详细功能文档.md)** - 完整的接口技术文档
- 🔒 **[隐私政策](PRIVACY.md)** - 数据隐私保护说明
- ⚖️ **[法律声明](LEGAL.md)** - 合规性和法律条款
- 📄 **[许可证](LICENSE)** - MIT开源许可证

---

### 💡 **使用提示**

1. **选择合适的工具**: 根据分析需求选择对应的专业工具
2. **查看详细文档**: 点击上方链接查看完整的接口文档和参数说明
3. **参数配置**: 按照工具界面提示正确配置参数
4. **数据分析**: 利用返回的Markdown表格和JSON数据进行分析

## 🎯 演示和示例

### 📋 **Dify 工作流演示**

我们提供了两个完整的 Dify 工作流演示文件，展示了如何使用 AKShare 股票数据插件的各种功能：

#### 🔧 **演示文件一：插件功能演示**
**文件**: `应用示例/AKShare 股票数据插件 CHATFLOW-DEMO.yml`

**功能说明**: 演示插件所有工具及其接口的使用，展示8个专业工具的完整功能

**演示内容**:
- **股票市场总貌** - 展示市场概况数据获取
- **个股信息总貌** - 演示个股详细信息查询
- **股票实时行情** - 实时价格数据获取
- **股票历史行情** - 历史价格数据分析
- **沪深港通持股** - 北向资金持股情况
- **资金流向分析** - 资金流向数据分析
- **股票财务数据分析** - 财务报表数据获取
- **股票技术分析** - 技术指标计算

**演示特色**:
- **智能条件分支** - 根据用户输入自动选择合适的数据接口
- **数据格式转换** - 自动将 Markdown 表格转换为 Excel 文件
- **多维度展示** - 涵盖所有8个专业工具的使用场景
- **完整工作流** - 从数据获取到结果展示的完整流程

#### 🤖 **演示文件二：个股深度分析应用**
**文件**: `应用示例/个股行情分析-ChatFlow.yml`

**功能说明**: 基于AKShare股票数据插件的个股深度分析ChatFlow应用，提供多维度股票分析

**核心功能**:
- **智能股票识别** - 自动识别股票代码和市场类型（沪市A股、深市A股、北交所）
- **历史行情分析** - 基于一年期历史数据的技术面分析
- **财务指标分析** - 基于财务数据的基本面分析
- **资金流向分析** - 基于资金流向的资金面分析
- **个股研报获取** - 获取最新的个股研究报告
- **综合投资建议** - 基于多维度数据的投资建议

**技术特色**:
- **动态日期计算** - 自动计算最新的历史数据时间范围
- **A股市场验证** - 智能识别并验证A股股票代码
- **多数据源整合** - 整合历史行情、财务数据、资金流向、研报等多维度数据
- **专业分析报告** - 生成包含技术面、基本面、资金面的综合分析报告

#### 🔧 **如何使用演示**
1. 在 Dify 平台中导入相应的演示文件
2. 确保已安装 AKShare 股票数据插件
3. 运行工作流，体验各种股票数据功能
4. 根据需要修改和定制工作流

### 📞 **技术支持**

如需详细的接口使用说明，请参考：
- 📖 **[详细功能文档](AKShare%20股票数据插件详细功能文档.md)** - 完整技术文档
- 🎯 **[工作流演示](应用示例/AKShare%20股票数据插件%20CHATFLOW-DEMO.yml)** - 完整演示示例
- 🔧 **插件配置文件** - tools目录下的各工具YAML配置
- 📚 **AKShare官方文档** - https://github.com/akfamily/akshare

---

**最后更新**: 2025-01-15  
**版本**: 0.5.1  
**作者**: AKShare 股票数据插件团队  
**许可证**: MIT License
