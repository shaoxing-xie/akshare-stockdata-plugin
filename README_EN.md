# AKShare Stock Data Plugin for Dify

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Dify Plugin](https://img.shields.io/badge/Dify-Plugin-green.svg)](https://dify.ai/)
[![AKShare](https://img.shields.io/badge/AKShare-Latest-blue.svg)](https://github.com/akfamily/akshare)

## 📞 Contact Information

- **Author**: shaoxing-xie
- **Email**: sxxiefg@163.com
- **Repository**: [https://github.com/shaoxing-xie/akshare-stockdata-plugin](https://github.com/shaoxing-xie/akshare-stockdata-plugin)
- **Issue Reports**: [GitHub Issues](https://github.com/shaoxing-xie/akshare-stockdata-plugin/issues)

## 📋 Overview

**AKShare Stock Data Plugin** is a comprehensive stock data tool developed specifically for the Dify platform, built on the renowned [AKShare](https://github.com/akfamily/akshare) Python library. This plugin provides users with a one-stop stock market data access solution, covering multiple dimensions of professional stock information including real-time quotes, historical data, financial analysis, capital flow, technical analysis, and Shanghai-Shenzhen-Hong Kong Stock Connect.

> **Feature Highlights**: Provides 78 professional tools and 190+ data interfaces, covering global stock markets. View the [Complete Function Documentation](https://github.com/shaoxing-xie/akshare-stockdata-plugin/blob/main/AKShare%20股票数据插件详细功能文档.md) for all interface details, parameter guides, and technical references.

> **Important Notice**: This plugin is a Dify platform integration tool based on the AKShare library. AKShare is an open-source financial data interface library designed for academic research purposes. We express our sincere gratitude to the AKShare project team for their excellent work.

> **⚠️ Interface Update Notice**: Due to network transmission stability issues, the following 8 shareholder analysis interfaces have been removed:
> - `stock_gdfx_free_holding_analyse_em` - Shareholder Holding Analysis (Top 10 Circulating Shareholders)
> - `stock_gdfx_holding_analyse_em` - Shareholder Holding Analysis (Top 10 Shareholders)
> - `stock_gdfx_free_holding_detail_em` - Shareholder Holding Details (Top 10 Circulating Shareholders)
> - `stock_gdfx_holding_detail_em` - Shareholder Holding Details (Top 10 Shareholders)
> - `stock_gdfx_free_holding_statistics_em` - Shareholder Holding Statistics (Top 10 Shareholders)
> - `stock_gdfx_holding_statistics_em` - Shareholder Holding Statistics (Top 10 Shareholders)
> - `stock_gdfx_free_holding_change_em` - Shareholder Holding Change Statistics (Top 10 Circulating Shareholders)
> - `stock_gdfx_holding_change_em` - Shareholder Holding Change Statistics (Top 10 Shareholders)
> 
> Other shareholder-related interfaces (Top 10 Shareholders, etc.) remain available.

## 🚀 Core Features

### 💎 **No API Key Required**
- ✅ **Zero Configuration**: No need to apply for any API keys or tokens
- ✅ **Plug and Play**: Ready to use immediately after installation, no complex configuration required
- ✅ **Cost Savings**: Completely free to use with no usage limits

### 🌐 **Authoritative Data Sources**
- 📊 **East Money (东方财富网)**: Real-time quotes, financial data, market analysis
- 📈 **Sina Finance (新浪财经)**: Historical quotes, stock news
- 🏢 **Tonghuashun (同花顺)**: Technical indicators, capital flow analysis
- 💰 **Tencent Finance (腾讯财经)**: Hong Kong and US stock data
- 📱 **NetEase Finance (网易财经)**: Market overview, individual stock information
- 🔗 **Public APIs**: Official stock exchange data interfaces

### 🛠️ **Powerful Feature Matrix**
- 🎯 **78 Professional Tools**: Covering all aspects of stock data analysis
  - **Categorized by Functional Domain**: Market overview, individual stock info, quote data, financial data, capital flow, technical analysis, and 12 major functional domains
  - **Fine-grained Design**: Each tool focuses on specific functionality for precise invocation
- 🌍 **190+ Data Interfaces**: Extensive coverage of major global stock markets
- 📊 **Multi-Market Support**: A-shares, B-shares, Hong Kong stocks, US stocks, STAR Market, Beijing Stock Exchange
- 🔄 **Real-time + Historical**: Both real-time quotes and historical data analysis
- 📋 **Dual Output**: Markdown tables + JSON format for easy reading and processing
- 📈 **Technical Analysis**: Professional technical indicator calculation and analysis tools

### 🔧 **Technical Advantages**
- 🛡️ **Smart Error Handling**: Automatic retry mechanism with graceful error recovery
- 🌐 **Full Unicode Support**: Perfect handling of Chinese characters and special symbols
- ⚡ **Performance Optimization**: Subprocess isolation and efficient memory management
- 🔄 **Parameter Validation**: Automatic parameter validation and format conversion

## 👥 Target Users

### 🎓 **Academic Researchers**
- Finance researchers conducting market analysis and academic studies
- Economics scholars studying stock market volatility patterns
- Data science researchers performing quantitative analysis

### 🤖 **AI Application Developers**
- Building intelligent investment assistants and financial chatbots
- Developing stock analysis and prediction models
- Creating automated investment decision systems

## 📥 Quick Download

[![Download Plugin](https://img.shields.io/badge/Download-Plugin%20Package-blue)](https://github.com/shaoxing-xie/akshare-stockdata-plugin/releases/tag/v0.7.0)

**Direct Download Latest Version Plugin Package** | [View All Versions](https://github.com/shaoxing-xie/akshare-stockdata-plugin/releases)

## 📦 How to Install

### Method 1: Direct Download Installation (Recommended)

[![Download Plugin](https://img.shields.io/badge/Download-Plugin%20Package-blue)](https://github.com/shaoxing-xie/akshare-stockdata-plugin/releases/tag/v0.7.0)

1. **Quick Download**: Click the button above to directly download the latest version plugin package
2. **Install in Dify**:
   - Open your Dify workspace
   - Navigate to **Tools** → **Plugins** → **Install Plugin**
   - Select **"Install from File"**
   - Upload the downloaded `.difypkg` file
   - Click the **Install** button

### Method 2: Download from Releases Directory
1. Visit the [releases directory](https://github.com/shaoxing-xie/akshare-stockdata-plugin/tree/main/releases)
2. Download the **"AKShare-Stockdata-plugin-v0.7.0.difypkg"** file
3. Follow the steps in Method 1 to install in Dify

### Method 3: Via GitHub Releases
1. Visit [GitHub Releases](https://github.com/shaoxing-xie/akshare-stockdata-plugin/releases)
2. Download the latest version plugin package
3. Follow the steps in Method 1 to install in Dify

### Method 4: Manual Installation
1. Clone this repository locally
   ```bash
   git clone https://github.com/shaoxing-xie/akshare-stockdata-plugin.git
   ```
2. Install Python dependencies
   ```bash
   cd akshare-stockdata-plugin
   pip install -r requirements.txt
   ```
3. Package the plugin using Dify CLI
   ```bash
   dify plugin package
   ```
4. Upload the generated .difypkg file in Dify

After installation, refer to the [Detailed Function Documentation](https://github.com/shaoxing-xie/akshare-stockdata-plugin/blob/main/AKShare%20股票数据插件详细功能文档.md) to quickly understand all interfaces.

## 🎯 How to Use

### Quick Start in Three Steps
1. **Select Tool**: Choose from 78 professional tools (categorized by functional domain)
2. **Select Interface**: Choose from 190+ data interfaces for specific data sources
3. **Set Parameters**: Configure stock codes, date ranges, and other parameters

### Usage Examples

#### Get Stock Historical Quotes
```json
{
  "interface": "East Money - A-Share Historical Market Data",
  "symbol": "600519",
  "period": "daily",
  "start_date": "20240101",
  "end_date": "20241231",
  "adjust": "qfq"
}
```

#### Get Real-time Quote Data
```json
{
  "interface": "East Money - Shanghai A-Share Real-time Market",
  "symbol": "600519"
}
```

#### Query Individual Stock Financial Data
```json
{
  "interface": "East Money - Performance Express - Balance Sheet",
  "date": "20240331"
}
```

## 🛠️ Tool Details

The plugin provides **78 professional tools**, categorized by functional domain as follows:

### 📊 **I. Market Overview Tools** (20 tools)
Get overall market overview and statistical data, including exchange market overview, equity pledge data, goodwill data, stock account statistics, IPO subscription, trading event notifications, institutional holdings, rating valuation, company announcements, dragon tiger list, block trading, margin trading, board data, stock hot data, limit up/down data, etc.

| Tool Name | Main Function | Use Cases |
|-----------|---------------|-----------|
| **Get Exchange Market Overview** | SSE and SZSE market overview data | Market analysis, macroeconomic research |
| **Get Equity Pledge Data** | Equity pledge market overview, listed company pledge ratio | Risk monitoring, pledge analysis |
| **Get Goodwill Data** | Goodwill market overview, individual stock goodwill details | Goodwill analysis, impairment monitoring |
| **Get Stock Account Statistics** | Stock account monthly statistics | Market participation analysis |
| **Get A-share Market Shareholder Number Data** | Shareholder number statistics | Shareholder structure analysis |
| **Get Stock Comment Data** | Stock comment data | Market sentiment analysis |
| **Get IPO Subscription Data** | IPO subscription and lottery data | IPO analysis, new stock strategy |
| **Get Trading Event Notifications** | Suspension/resumption, dividend alerts | Trading alerts, event monitoring |
| **Get Market Institutional Holdings Data** | Institutional holdings overview, recommendation pool | Institutional trend analysis |
| **Get Stock Rating and Valuation** | Stock rating records, valuation analysis | Investment rating, valuation research |
| **Get Company Announcements** | Company news, important announcements | Company event tracking |
| **Get Company Disclosure** | Company disclosure data | Disclosure analysis |
| **Get Stock List Data** | Shanghai-Shenzhen-Beijing A-share stock codes and names | Stock list query |
| **Get Dragon Tiger List** | Dragon tiger list trading data | Capital flow analysis |
| **Get Block Trading** | Block trading data | Large transaction analysis |
| **Get A-share Market Margin Trading** | Margin trading data | Leverage capital analysis |
| **Get Flush Board Data** | Flush concept and industry board data | Board analysis, thematic investment |
| **Get East Money Board Data** | East Money concept and industry board data | Board analysis, industry research |
| **Get A-share Market Stock Hot Data** | Stock hot rankings | Market hot analysis |
| **Get A-share Market Limit Up/Down Data** | Limit up/down data | Limit up analysis, risk monitoring |

### 🏢 **II. Individual Stock Information Tools** (6 tools)
Get individual stock basic information, news research, dividend information, shareholder holding changes, shareholder numbers, stock issuance and listing data, etc.

| Tool Name | Main Function | Use Cases |
|-----------|---------------|-----------|
| **Get Stock Basic Info** | Stock information, main business introduction, main business composition, company profile | Fundamental analysis, company research |
| **Get Stock News Research** | News information, individual stock research reports | Information tracking, research analysis |
| **Get Stock Dividend Info** | Dividend distribution details, historical dividends | Dividend analysis, dividend investment |
| **Get Shareholder Holding Changes** | Top 10 shareholders, top 10 circulating shareholders, holding changes | Shareholder structure analysis |
| **Get A-share Shareholder Number Detail** | Shareholder number detail data | Shareholder dispersion analysis |
| **Get Stock Issuance and Release** | New stock issuance, stock additional issuance, restricted share release | Issuance and listing analysis |

### 📈 **III. Quote Data Tools** (8 tools)
Get real-time quotes, historical quotes, intraday quotes, comparison data for various markets, etc.

| Tool Name | Main Function | Use Cases |
|-----------|---------------|-----------|
| **Get Stock Real-time Quote** | Individual stock real-time quote | Real-time monitoring, trading decisions |
| **Get Stock Historical Quotes** | A-share daily and minute data | Technical analysis, backtesting research |
| **Get Stock Intraday Quotes** | Intraday minute data, minute data | Intraday analysis, order book analysis |
| **Get Stock Peer Comparison** | Growth, valuation, DuPont analysis, company size comparison | Industry comparison, valuation analysis |
| **Get A-share Market Stock Quotes** | Shanghai-Shenzhen-Beijing A-share real-time quotes | Market quote monitoring |
| **Get A-share Board Quotes** | New stocks, ChiNext, STAR Market real-time quotes | Board quote analysis |
| **Get Stock Comparison Quotes** | AH share comparison, AB share comparison | Cross-market comparison |
| **Get Special Stock Quotes** | Sub-new stocks, two networks and delisted stocks | Special stock analysis |

### 💰 **IV. Financial Data Tools** (6 tools)
Get financial statements and performance data, including performance reports, balance sheets, profit statements, cash flow statements, financial indicators, etc.

| Tool Name | Main Function | Use Cases |
|-----------|---------------|-----------|
| **Get Stock Performance Reports** | Performance statements, performance reports, performance forecasts | Performance analysis, performance tracking |
| **Get Stock Balance Sheet** | Balance sheet data | Financial analysis, solvency analysis |
| **Get Stock Profit Sheet** | Profit statement data | Profitability analysis |
| **Get Stock Cash Flow Sheet** | Cash flow statement data | Cash flow analysis |
| **Get Stock Financial Indicators** | Financial indicator data | Financial indicator analysis |
| **Get Stock Financial Analysis Indicators** | Financial analysis indicator data | Comprehensive financial analysis |

### 🌊 **V. Capital Flow Tools** (6 tools)
Analyze capital flow and market sentiment, including individual stock capital flow, board capital flow, main force capital flow, chip distribution, etc.

| Tool Name | Main Function | Use Cases |
|-----------|---------------|-----------|
| **Get Stock Fund Flow** | Individual stock fund flow data | Capital flow analysis |
| **Get Stock Chip Distribution** | Chip distribution data | Chip analysis |
| **Get Market Stock Fund Flow Rank** | Fund flow ranking data | Fund flow analysis |
| **Get Market Fund Flow History** | Fund flow historical data | Fund flow trend analysis |
| **Get Sector Fund Flow Rank** | Sector fund flow rankings | Sector capital analysis |
| **Get Big Deal Tracking** | Big deal tracking data | Main force trend tracking |

### 📈 **VI. Technical Analysis Tools** (7 tools)
Technical indicators and innovation high/low data, including innovation highs/lows, continuous rise/fall, volume analysis, breakthrough analysis, price-volume analysis, ESG ratings, etc.

| Tool Name | Main Function | Use Cases |
|-----------|---------------|-----------|
| **Get Technical Innovation High Low** | Innovation high, innovation low stocks | Technical stock selection, trend analysis |
| **Get Technical Continuous Rise Fall** | Continuous rise, continuous fall stocks | Trend analysis, reversal analysis |
| **Get Technical Volume Analysis** | Continuous volume increase, continuous volume decrease stocks | Volume-price analysis |
| **Get Technical Breakthrough Analysis** | Upward breakthrough, downward breakthrough stocks | Breakthrough analysis, trend judgment |
| **Get Technical Price Volume Analysis** | Price-volume rise, price-volume fall stocks | Price-volume relationship analysis |
| **Get Technical Insurance Disclosure** | Insurance capital placard raising data | Insurance capital trends |
| **Get ESG Rating Data** | ESG rating data | ESG investment, social responsibility investment |

### 📉 **VII. Technical Indicator Tools** (5 tools) ⭐ **Extended Indicator Tools**
Comprehensive analysis tools based on individual stock historical data calculating various technical indicators.

| Tool Name | Main Function | Use Cases |
|-----------|---------------|-----------|
| **Get Stock Trend Momentum Daily** | Daily technical indicator calculation | Technical analysis, quantitative research |
| **Get Stock Trend Momentum Minute** | Minute-level technical indicator calculation | High-frequency analysis, intraday trading |
| **Get Stock Dynamic Valuation** | Dynamic valuation indicators | Valuation analysis, investment decisions |
| **Get Stock Historical Valuation** | Historical valuation indicators | Valuation trend analysis |
| **Get Stock Basic Info Summary** | Individual stock basic information summary | Comprehensive information query |

### 🔗 **VIII. HSGT Tools** (4 tools)
Northbound capital holdings and flow data, including exchange rate data, capital flow, ranking data, individual stock holdings, etc.

| Tool Name | Main Function | Use Cases |
|-----------|---------------|-----------|
| **Get HSGT Exchange Rate Data** | Hong Kong Stock Connect exchange rate data | Exchange rate analysis, cross-border capital analysis |
| **Get HSGT Fund Flow Data** | Fund flow data | Foreign capital trend analysis |
| **Get HSGT Ranking Data** | Sector rankings, stock rankings | Foreign capital holdings analysis |
| **Get HSGT Individual Holdings** | Specific stock holdings data | Individual stock foreign capital holdings analysis |

### 📊 **IX. Index Data Tools** (3 tools) ⭐ **Index Analysis Tools**
A-share index-related data interfaces, including index real-time quotes, historical data, technical indicators, etc.

| Tool Name | Main Function | Use Cases |
|-----------|---------------|-----------|
| **Get Index Spot Quotes** | Index real-time quote data | Index monitoring, market trends |
| **Get Index Historical Quotes** | Index historical quote data | Index analysis, technical research |
| **Get Index Trend Momentum Daily** | Index technical indicator calculation | Index technical analysis |

### 🇭🇰 **X. Hong Kong Stock Data Tools** (8 tools) ⭐ **Independent Tools**
Hong Kong stock-related data interfaces, including Hong Kong stock real-time quotes, historical data, financial analysis, company information, dividend information, etc.

| Tool Name | Main Function | Use Cases |
|-----------|---------------|-----------|
| **Get HK Individual Info** | Hong Kong stock individual basic information | Hong Kong stock fundamental analysis |
| **Get HK Historical Quotes** | Hong Kong stock historical quote data | Hong Kong stock technical analysis |
| **Get HK Daily Minute Quotes** | Hong Kong stock minute quote data | Hong Kong stock intraday analysis |
| **Get HK Dividend Payout** | Hong Kong stock dividend payout data | Hong Kong stock dividend analysis |
| **Get HK Financial Indicators** | Hong Kong stock financial indicator data | Hong Kong stock financial analysis |
| **Get HK Financial Statements** | Hong Kong stock financial statement data | Hong Kong stock financial statement analysis |
| **Get HK Industry Comparison** | Hong Kong stock industry comparison data | Hong Kong stock industry comparison |
| **Get HK Spot Quotes** | Hong Kong stock real-time quote data | Hong Kong stock real-time monitoring |

### 🇺🇸 **XI. US Stock Data Tools** (5 tools) ⭐ **Independent Tools**
US stock-related data interfaces, including US stock real-time quotes, historical data, financial analysis, etc.

| Tool Name | Main Function | Use Cases |
|-----------|---------------|-----------|
| **Get US Spot Quotes** | US stock real-time quote data | US stock real-time monitoring |
| **Get US Historical Quotes** | US stock historical quote data | US stock technical analysis |
| **Get US Daily Minute Quotes** | US stock minute quote data | US stock intraday analysis |
| **Get US Financial Indicators** | US stock financial indicator data | US stock financial analysis |
| **Get US Financial Statements** | US stock financial statement data | US stock financial statement analysis |

---

**Tool Statistics**:
- **Total**: 78 professional tools
- **Data Interfaces**: 190+ data interfaces
- **Functional Coverage**: Market overview, individual stock info, quote data, financial data, capital flow, technical analysis, technical indicators, HSGT, index data, Hong Kong stock data, US stock data, and 12 major functional domains

## 🔒 Privacy & Security

This plugin strictly adheres to data privacy protection principles:
- ✅ **No User Data Storage**: All data is processed only in memory, no persistent storage
- ✅ **No Personal Information Collection**: Does not obtain or transmit any user personal sensitive information  
- ✅ **Transparent Data Processing**: All data sources and processing procedures are completely transparent
- ✅ **Open Source Auditable**: Source code is completely open for review and verification

For detailed information, please refer to [Privacy Policy](PRIVACY.md)

## ⚖️ Compliance Statement

This plugin fully complies with relevant laws and regulations:
- 📋 **Open Source Compliance**: Open source project based on MIT license
- 🌐 **Data Compliance**: Only uses publicly accessible data sources
- 🔍 **Transparent Operations**: Data acquisition methods and processing procedures are completely transparent
- ⚖️ **Legal Compliance**: Strictly adheres to relevant financial data usage regulations

For detailed information, please refer to [Legal Notice](LEGAL.md)

## 🙏 Acknowledgments

### AKShare Project Team
This plugin is built on the excellent [AKShare](https://github.com/akfamily/akshare) library. We extend our sincere gratitude to:
- **AKShare Development Team**: For creating and maintaining this comprehensive financial data interface library
- **Open Source Community Contributors**: For valuable contributions to the project's development

### Dify Platform
Thanks to the [Dify](https://dify.ai/) team for providing an excellent AI application development platform that makes AI applications for financial data more convenient.

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

**Note**: This plugin is a wrapper tool for the AKShare library. For underlying data access functionality, please refer to AKShare's MIT license terms.

## 🤝 Contributing

We welcome community contributions! Please follow these steps to participate:

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Create a Pull Request

## 📞 Technical Support

If you encounter problems or have suggestions:
1. Check the [Issues](https://github.com/shaoxing-xie/akshare-stockdata-plugin/issues) page
2. Create a new issue with detailed information
3. Refer to AKShare official documentation

## 🔄 Version Upgrade

### Upgrading from 0.6.0 to 0.7.0
- ✅ **Tool Split Optimization**: Split from 12 large tools into 78 fine-grained tools for more precise invocation
- ✅ **Functional Domain Classification**: Displayed by functional domain for easier search and use
- ✅ **Fully Backward Compatible**: All workflows based on version 0.6.0 can be used directly without modification
- ✅ **Feature Enhancement**: More data interfaces and features

👉 **[Detailed Upgrade Guide](UPGRADE_GUIDE.md)** - Complete version upgrade instructions

## 🔧 Troubleshooting

### ❌ **Common Issues and Solutions**

#### 1. **Plugin Not Displayed in Dify Tools After Installation**
**Symptoms**: After plugin installation, the plugin is not visible in Dify's tool list

**Possible Causes and Solutions**:

**Case 1: Pre-compilation Not Yet Complete**
- ⏰ **Check Pre-compilation Status**: Check Dify backend plugin running logs to confirm if pre-compilation is still in progress
- 📊 **Monitor Progress**: Pre-compilation process usually takes 5-15 minutes, please wait patiently
- 🔍 **View Logs**: Check plugin running logs in Dify admin backend to confirm compilation progress

**Case 2: Pre-compilation Complete But Tools Not Displayed**
- 🔄 **Reinstall**: After pre-compilation is complete, if the plugin is still not displayed in Dify tools, please install the plugin package again, and the plugin will display normally
- ✅ **Normal Behavior**: This is a known issue with Dify plugin system, reinstalling will resolve it

**Technical Notes**:
- Pre-compilation timeout setting: 30 minutes (sufficient to complete compilation)
- Optimized `.difyignore` file to exclude test files and speed up compilation
- This is a common issue with Dify plugin system that may affect all plugins

#### 2. **Tool Call Returns Empty Data**
**Symptoms**: Tool call succeeds but returns `{"data": []}`

**Possible Causes**:
- Network connection issues
- Data source temporarily unavailable
- Parameter configuration errors

**Solutions**:
- Check network connection
- Increase retry count and timeout duration
- Verify parameter format (date format: YYYYMMDD)

#### 3. **Dify 0.3.0+ Compatibility Issues**
**Symptoms**: Plugin cannot work properly in newer versions of Dify

**Solutions**:
- Ensure using the latest version plugin package
- Check `.env` file configuration:
  ```env
  FORCE_VERIFYING_SIGNATURE=false
  PLUGIN_PYTHON_ENV_INIT_TIMEOUT=600
  ```

## 📚 Detailed Function Documentation

The plugin provides 78 professional tools with 190+ data interfaces. To keep the README concise, detailed interface documentation has been separated into a dedicated technical document:

### 📖 **Complete Technical Documentation**
👉 **[AKShare Stock Data Plugin Detailed Function Documentation.md](https://github.com/shaoxing-xie/akshare-stockdata-plugin/blob/main/AKShare%20股票数据插件详细功能文档.md)** - Your Interface Reference!

This document contains:
- ✅ **190+ interface complete descriptions** - Function, parameters, and AKShare reference information for each interface
- ✅ **78 tools detailed classification** - Complete tool list categorized by functional domain  
- ✅ **Parameter usage guide** - Detailed parameter input instructions and format requirements
- ✅ **Technical reference information** - Complete AKShare interface references and target URLs

### 🎯 **Quick Navigation (Categorized by Functional Domain)**
- [I. Market Overview Tools (20 tools)](AKShare%20股票数据插件详细功能文档.md#一市场总貌类工具)
- [II. Individual Stock Information Tools (6 tools)](AKShare%20股票数据插件详细功能文档.md#二个股信息类工具)
- [III. Quote Data Tools (8 tools)](AKShare%20股票数据插件详细功能文档.md#三行情数据类工具)
- [IV. Financial Data Tools (6 tools)](AKShare%20股票数据插件详细功能文档.md#四财务数据类工具)
- [V. Capital Flow Tools (6 tools)](AKShare%20股票数据插件详细功能文档.md#五资金流向类工具)
- [VI. Technical Analysis Tools (7 tools)](AKShare%20股票数据插件详细功能文档.md#六技术分析类工具)
- [VII. Technical Indicator Tools (5 tools)](AKShare%20股票数据插件详细功能文档.md#七技术指标类工具) ⭐ **Extended Indicator Tools**
- [VIII. HSGT Tools (4 tools)](AKShare%20股票数据插件详细功能文档.md#八沪深港通类工具)
- [IX. Index Data Tools (3 tools)](AKShare%20股票数据插件详细功能文档.md#九指数数据类工具) ⭐ **Index Analysis Tools**
- [X. Hong Kong Stock Data Tools (8 tools)](AKShare%20股票数据插件详细功能文档.md#十港股数据类工具) ⭐ **Independent Tools**
- [XI. US Stock Data Tools (5 tools)](AKShare%20股票数据插件详细功能文档.md#十一美股数据类工具) ⭐ **Independent Tools**

## 🎯 Demo and Examples

### 📋 **Dify Workflow Demo**

We provide two complete Dify workflow demo files that showcase how to use various features of the AKShare Stock Data Plugin:

#### 🔧 **Demo File 1: Plugin Functionality Demo**
**File**: `应用示例/AKShare 股票数据插件 CHATFLOW-DEMO.yml`

**Description**: Demonstrates the usage of all plugin tools and their interfaces, showcasing the complete functionality of 78 professional tools

**Demo Content**:
- **Stock Market Summary** - Market overview data acquisition
- **Individual Stock Information Summary** - Individual stock detailed information queries
- **Real-time Stock Quotes** - Real-time price data acquisition
- **Historical Stock Quotes** - Historical price data analysis
- **Shanghai-Shenzhen-Hong Kong Stock Connect Holdings** - Northbound capital holdings
- **Capital Flow Analysis** - Capital flow data analysis
- **Stock Financial Data Analysis** - Financial statement data acquisition
- **Stock Technical Analysis** - Technical indicator calculations

**Demo Features**:
- **Smart Conditional Branching** - Automatically selects appropriate data interfaces based on user input
- **Data Format Conversion** - Automatically converts Markdown tables to Excel files
- **Multi-dimensional Display** - Covers usage scenarios for all 78 professional tools
- **Complete Workflow** - Complete process from data acquisition to result display

#### 🤖 **Demo File 2: Individual Stock Deep Analysis Application**
**File**: `应用示例/个股行情分析-ChatFlow.yml`

**Description**: Individual stock deep analysis ChatFlow application based on AKShare Stock Data Plugin, providing multi-dimensional stock analysis

**Core Features**:
- **Intelligent Stock Recognition** - Automatically identifies stock codes and market types (Shanghai A-share, Shenzhen A-share, Beijing Stock Exchange)
- **Historical Quote Analysis** - Technical analysis based on one-year historical data
- **Financial Indicator Analysis** - Fundamental analysis based on financial data
- **Fund Flow Analysis** - Fund flow analysis based on capital flow data
- **Individual Stock Research Reports** - Access to latest individual stock research reports
- **Comprehensive Investment Recommendations** - Investment recommendations based on multi-dimensional data

**Technical Features**:
- **Dynamic Date Calculation** - Automatically calculates the latest historical data time range
- **A-share Market Validation** - Intelligently identifies and validates A-share stock codes
- **Multi-data Source Integration** - Integrates historical quotes, financial data, fund flow, research reports and other multi-dimensional data
- **Professional Analysis Reports** - Generates comprehensive analysis reports including technical, fundamental, and fund flow aspects

#### 🔧 **How to Use the Demo**
1. Import the corresponding demo file in the Dify platform
2. Ensure the AKShare Stock Data Plugin is installed
3. Run the workflow to experience various stock data features
4. Modify and customize the workflow as needed

### 📞 **Support**

For detailed interface usage instructions, please refer to:
- 📖 **[Detailed Function Documentation](AKShare%20股票数据插件详细功能文档.md)** - Complete technical documentation
- 🎯 **[Workflow Demo](应用示例/AKShare%20股票数据插件%20CHATFLOW-DEMO.yml)** - Complete demo example
- 🔧 **Plugin Configuration Files** - YAML configurations for each tool in the tools directory
- 📚 **AKShare Official Documentation** - https://github.com/akfamily/akshare

---

**Last Updated**: 2025-11-06  
**Version**: 0.7.0  
**Author**: AKShare Stock Data Plugin Team  
**License**: MIT License