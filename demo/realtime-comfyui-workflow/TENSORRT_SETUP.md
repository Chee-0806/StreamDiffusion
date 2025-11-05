# TensorRT 加速设置指南

## 当前状态

从日志可以看到：
```
ModuleNotFoundError: No module named 'polygraphy'
Acceleration has failed. Falling back to normal mode.
```

**这意味着 TensorRT 加速实际上没有启用**，程序回退到了正常模式（无加速），所以速度较慢。

## 解决方案

### 方案 1: 使用 xformers（推荐，最简单）

xformers 通常已经安装，直接使用即可：

```bash
python main.py --port 6006 --host 0.0.0.0 \
    --model-path "stabilityai/sd-turbo" \
    --acceleration xformers
```

xformers 提供良好的加速效果，且无需额外配置。

### 方案 2: 安装 TensorRT 依赖（需要额外步骤）

如果需要使用 TensorRT 获得最佳性能，需要安装以下依赖：

#### 步骤 1: 安装 StreamDiffusion with TensorRT

```bash
# 如果使用 git 安装
pip install git+https://github.com/cumulo-autumn/StreamDiffusion.git@main#egg=streamdiffusion[tensorrt]

# 或者使用稳定版本
pip install streamdiffusion[tensorrt]
```

#### 步骤 2: 安装 TensorRT 扩展

```bash
python -m streamdiffusion.tools.install-tensorrt
```

这个命令会自动安装：
- `polygraphy`
- `onnx-graphsurgeon`
- `nvidia-tensorrt`

#### 步骤 3: 验证安装

运行程序后，如果看到类似以下日志，说明 TensorRT 已启用：
```
Using TensorRT acceleration...
Building engine...
```

而不是：
```
ModuleNotFoundError: No module named 'polygraphy'
Acceleration has failed. Falling back to normal mode.
```

## 性能对比

| 加速方式 | 速度 | 安装难度 | 推荐场景 |
|---------|------|---------|---------|
| **正常模式** | 最慢 | 无需安装 | 调试用 |
| **xformers** | 快 | 简单（通常已安装） | 推荐日常使用 ✅ |
| **tensorrt** | 最快 | 需要额外安装 | 生产环境追求极致性能 |

## 注意事项

1. **TensorRT 首次运行慢**: 首次使用 TensorRT 时需要构建引擎，可能需要几分钟
2. **引擎缓存**: 构建完成后，引擎会保存在 `engines/` 目录，后续运行会直接使用
3. **GPU 内存**: TensorRT 需要更多 GPU 内存来存储引擎
4. **兼容性**: TensorRT 对 CUDA 版本有要求，确保 CUDA 版本兼容

## 当前推荐

**建议使用 xformers**，因为：
- ✅ 通常已经安装
- ✅ 提供良好的加速效果
- ✅ 无需额外配置
- ✅ 稳定可靠

如果确实需要最高性能，再考虑安装 TensorRT。

