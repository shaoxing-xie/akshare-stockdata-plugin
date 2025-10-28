# 本地开发环境配置

## 性能优化配置

### 跳过子进程调用（推荐用于本地开发）

在本地开发时，可以通过设置环境变量来跳过子进程调用，直接调用AKShare接口，这样可以避免子进程开销，提高性能：

```bash
# Windows PowerShell
$env:AKSHARE_USE_SUBPROCESS="false"
python -m main

# Linux/macOS
export AKSHARE_USE_SUBPROCESS=false
python -m main
```

### 为什么需要子进程？

在生产环境（Docker容器）中，我们使用子进程调用AKShare接口是为了：
1. 避免gevent与AKShare的冲突
2. 提供更好的错误隔离
3. 支持超时控制

但在本地开发环境中，这些限制通常不存在，直接调用可以获得更好的性能。

### 性能对比

- **子进程模式**：适合生产环境，有额外的进程创建和数据序列化开销
- **直接调用模式**：适合本地开发，性能更好，调试更方便

### 注意事项

- 直接调用模式仅在本地开发时推荐使用
- 生产环境必须使用子进程模式以确保稳定性
- 如果遇到gevent相关错误，请切换回子进程模式
