# TensorRT CUDA 错误 35 修复方案

## 问题原因

**CUDA 初始化错误 35** 的根本原因是：
- PyTorch 使用 CUDA 11.7
- 之前安装的 TensorRT 10.x 需要 CUDA 12
- 版本不匹配导致 TensorRT 无法初始化

## 解决方案

### ✅ 已修复：安装匹配的 TensorRT 版本

使用 StreamDiffusion 的官方安装工具，它会自动安装匹配 CUDA 11 的 TensorRT 9.x：

```bash
source /root/autodl-tmp/venv/bin/activate
cd /root/StreamDiffusion
python -m streamdiffusion.tools.install-tensorrt
```

这会安装：
- TensorRT 9.0.1.post11.dev4（匹配 CUDA 11）
- nvidia-cudnn-cu11==8.9.4.25
- polygraphy（如果未安装）
- onnx-graphsurgeon（如果未安装）

## 关键配置

### 1. 环境变量设置（已在 start.sh 中配置）

```bash
# CUDA 环境
export CUDA_HOME=/usr/local/cuda-12
export PATH=/usr/local/cuda-12/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-12/lib64:$LD_LIBRARY_PATH

# TensorRT 库路径
export LD_LIBRARY_PATH=/root/autodl-tmp/venv/lib/python3.10/site-packages/tensorrt_libs:$LD_LIBRARY_PATH

# CUDA 模块加载
export CUDA_MODULE_LOADING=LAZY
```

### 2. 代码修复（已在 wrapper.py 中添加）

在初始化 TensorRT 之前，先初始化 PyTorch 的 CUDA 上下文：

```python
import torch
if torch.cuda.is_available():
    _ = torch.cuda.current_device()
    torch.cuda.init()
    dummy = torch.randn(1, device="cuda")
    del dummy
    torch.cuda.synchronize()
```

## 验证安装

运行以下命令验证 TensorRT 是否正常工作：

```bash
source /root/autodl-tmp/venv/bin/activate
export TRT_LIB_PATH=/root/autodl-tmp/venv/lib/python3.10/site-packages/tensorrt_libs
export CUDA_HOME=/usr/local/cuda-12
export LD_LIBRARY_PATH=$TRT_LIB_PATH:$CUDA_HOME/lib64:$LD_LIBRARY_PATH

python << 'EOF'
import torch
torch.cuda.init()
dummy = torch.randn(1, device="cuda")
del dummy
torch.cuda.synchronize()

import tensorrt as trt
builder = trt.Builder(trt.Logger(trt.Logger.ERROR))
print('✓ TensorRT 正常工作！')
EOF
```

## 版本信息

- **PyTorch CUDA**: 11.7
- **TensorRT**: 9.0.1.post11.dev4（匹配 CUDA 11）
- **cuda-python**: 12.4.0
- **polygraphy**: 0.49.26
- **onnx-graphsurgeon**: 0.5.8

## 注意事项

1. **首次运行慢**: TensorRT 首次运行时需要构建引擎，可能需要几分钟
2. **引擎缓存**: 构建完成后，引擎保存在 `engines/` 目录
3. **版本匹配**: 确保 TensorRT 版本与 PyTorch 的 CUDA 版本匹配

## 如果仍然遇到问题

1. 检查 TensorRT 版本：`python -c "import tensorrt; print(tensorrt.__version__)"`
2. 应该显示 `9.0.1.post11.dev4` 或类似版本（匹配 CUDA 11）
3. 如果版本不对，重新运行安装工具

