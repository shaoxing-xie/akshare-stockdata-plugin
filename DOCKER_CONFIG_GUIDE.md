# Docker环境配置指南

## 问题说明

如果遇到技术指标计算库安装失败的问题，请参考以下配置方案。

## 方案1：增加资源限制（推荐）

在Dify的`docker-compose.yml`中增加以下配置：

```yaml
services:
  dify-api:
    environment:
      # 增加插件安装超时时间（30分钟）
      - PLUGIN_INSTALL_TIMEOUT=1800
      # 增加pip超时和重试
      - PIP_TIMEOUT=600
      - PIP_RETRIES=3
      # 网络超时配置
      - HTTP_TIMEOUT=300
      - CONNECT_TIMEOUT=60
      - READ_TIMEOUT=300
    deploy:
      resources:
        limits:
          memory: 4G        # 增加内存限制
          cpus: '2.0'       # 增加CPU限制
        reservations:
          memory: 2G
          cpus: '1.0'
```

## 方案2：使用预构建镜像

创建一个包含技术分析库的Python基础镜像：

```dockerfile
# 创建文件：Dockerfile.talib
FROM python:3.12-slim

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    make \
    wget \
    autoconf \
    automake \
    libtool \
    libopenblas-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装TA-Lib C库
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib-0.4.0/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib-0.4.0 ta-lib-0.4.0-src.tar.gz

# 安装Python技术分析库
RUN pip install --no-cache-dir \
    TA-Lib==0.4.28 \
    pandas-ta>=0.3.14b \
    numpy>=1.21.0

# 设置环境变量
ENV LD_LIBRARY_PATH=/usr/lib
```

## 方案3：降级到基础版本（默认）

如果以上方案不可行，插件会自动使用pandas内置函数计算技术指标，无需额外配置。

## 优势说明

### 使用pandas内置函数（当前默认）
- ✅ **零配置安装**：无需编译环境
- ✅ **广泛兼容性**：支持所有Dify部署方式
- ✅ **功能完整**：技术指标计算准确
- ✅ **性能良好**：pandas向量化计算
- ✅ **维护简单**：减少依赖问题

### 使用TA-Lib（可选）
- ✅ **计算精度高**：专业级技术分析库
- ✅ **功能丰富**：支持更多技术指标
- ❌ **需要编译环境**：需要C编译器
- ❌ **安装复杂**：可能遇到依赖问题

## 推荐配置

对于大多数用户，推荐使用**方案3（pandas内置函数）**，因为：

1. **开箱即用**：无需任何额外配置
2. **稳定可靠**：不会因为依赖问题导致安装失败
3. **功能完整**：满足股票分析的基本需求
4. **维护简单**：减少技术支持成本

## 技术支持

如果遇到问题，请：

1. 检查Docker资源限制是否足够
2. 确认网络连接是否正常
3. 查看Dify日志中的具体错误信息
4. 考虑使用pandas内置函数版本

## 版本说明

- **v0.5.1**：默认使用pandas内置函数，确保广泛兼容性
- **v0.5.0**：使用TA-Lib，需要编译环境
