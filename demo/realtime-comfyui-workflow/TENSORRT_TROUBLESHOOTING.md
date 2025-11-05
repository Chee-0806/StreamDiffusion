# TensorRT 故障排除指南

## 当前遇到的问题

### CUDA 初始化错误 35

从日志中看到：
```
[E] createInferBuilder: Error Code 6: API Usage Error (CUDA initialization failure with error: 35)
```

**错误原因**：
- CUDA 驱动版本：12.6
- PyTorch CUDA 版本：11.7
- 版本不匹配导致 TensorRT 无法初始化

## 解决方案

### 方案 1: 使用 xformers（推荐 ✅）

xformers 更稳定，兼容性更好，且无需额外配置：

```bash
# 修改 start.sh 中的加速方式
--acceleration xformers
```

**优点**：
- ✅ 稳定可靠
- ✅ 兼容性好
- ✅ 无需额外配置
- ✅ 提供良好的加速效果

### 方案 2: 修复 CUDA 环境（如果必须使用 TensorRT）

1. **设置 CUDA 环境变量**（已在 start.sh 中添加）：

```bash
export CUDA_HOME=/usr/local/cuda-12
export PATH=/usr/local/cuda-12/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12/lib64:$LD_LIBRARY_PATH
```

2. **检查 CUDA 库**：

```bash
# 检查 CUDA 运行时库
ls -la /usr/local/cuda-12/lib64/libcudart.so*

# 检查 TensorRT 库
python -c "import tensorrt; print(tensorrt.__file__)"
```

3. **如果仍然失败**，可能需要：
   - 重新安装 PyTorch（匹配 CUDA 12.x）
   - 或使用 Docker 容器（已配置好 CUDA 环境）

## 当前配置

- **加速方式**: `xformers`（已修改）
- **原因**: TensorRT 在当前环境中遇到 CUDA 版本不匹配问题

## 性能对比

| 加速方式 | 速度 | 稳定性 | 兼容性 | 推荐度 |
|---------|------|--------|--------|--------|
| **xformers** | 快 | 高 | 优秀 | ⭐⭐⭐⭐⭐ |
| **tensorrt** | 最快 | 中 | 需要匹配 CUDA 版本 | ⭐⭐⭐ |
| **正常模式** | 慢 | 高 | 完美 | ⭐⭐ |

## 建议

**强烈建议使用 xformers**，因为：
1. 在当前环境中 TensorRT 遇到了 CUDA 版本兼容性问题
2. xformers 已经足够快，提供良好的加速效果
3. 无需复杂的 CUDA 环境配置
4. 更稳定可靠

如果未来需要最高性能，可以考虑：
- 使用 Docker 容器（已预配置 CUDA 环境）
- 或重新安装匹配的 PyTorch 和 CUDA 版本

