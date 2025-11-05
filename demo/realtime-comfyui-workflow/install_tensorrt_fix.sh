#!/bin/bash
# 修复 TensorRT 安装脚本
# 使用虚拟环境安装

echo "=========================================="
echo "TensorRT 安装修复脚本"
echo "=========================================="
echo ""

# 激活虚拟环境
source /root/autodl-tmp/venv/bin/activate
echo "✓ 已激活虚拟环境: $(which python)"
echo ""

# 1. 安装 nvidia-cuda-runtime（如果未安装）
echo "1. 检查并安装 nvidia-cuda-runtime..."
if ! python -c "import nvidia.cuda.runtime" 2>/dev/null; then
    pip install nvidia-cuda-runtime --no-cache-dir
    echo "   ✓ nvidia-cuda-runtime 已安装"
else
    echo "   ✓ nvidia-cuda-runtime 已存在"
fi
echo ""

# 2. 检查 polygraphy 和 onnx-graphsurgeon
echo "2. 检查 polygraphy 和 onnx-graphsurgeon..."
if python -c "import polygraphy" 2>/dev/null; then
    echo "   ✓ polygraphy 已安装"
else
    echo "   ✗ polygraphy 未安装，正在安装..."
    pip install polygraphy --no-cache-dir
fi

if python -c "import onnx_graphsurgeon" 2>/dev/null; then
    echo "   ✓ onnx-graphsurgeon 已安装"
else
    echo "   ✗ onnx-graphsurgeon 未安装，正在安装..."
    pip install onnx-graphsurgeon --no-cache-dir
fi
echo ""

# 3. 安装 cuda-python（TensorRT 需要，必须使用 12.4.0 版本）
echo "3. 检查并安装 cuda-python..."
if python -c "from cuda import cudart" 2>/dev/null; then
    echo "   ✓ cuda-python 已安装"
else
    echo "   ✗ cuda-python 未安装或版本不对，正在安装 12.4.0 版本..."
    pip uninstall -y cuda-python 2>/dev/null || true
    pip install cuda-python==12.4.0 --no-cache-dir
    echo "   ✓ cuda-python 12.4.0 已安装"
fi
echo ""

# 4. 安装 TensorRT（使用官方工具，自动匹配 CUDA 版本）
echo "4. 安装 TensorRT..."
if python -c "import tensorrt as trt" 2>/dev/null; then
    trt_version = python -c "import tensorrt as trt; print(trt.__version__)" 2>/dev/null
    echo "   ✓ TensorRT 已安装，版本: $trt_version"
    
    # 检查版本是否匹配（PyTorch CUDA 11 需要 TensorRT 9.x）
    pytorch_cu = python -c "import torch; print(torch.version.cuda.split('.')[0])" 2>/dev/null
    if [ "$pytorch_cu" = "11" ] && [ "$(echo $trt_version | cut -d. -f1)" != "9" ]; then
        echo "   ⚠ TensorRT 版本可能不匹配 PyTorch CUDA 版本"
        echo "   正在重新安装匹配的版本..."
        pip uninstall -y tensorrt tensorrt_cu13 tensorrt_cu13_libs tensorrt_cu13_bindings 2>/dev/null || true
        cd /root/StreamDiffusion
        python -m streamdiffusion.tools.install-tensorrt 2>&1 | grep -E "Installing|Successfully" | tail -5
    fi
else
    echo "   - 使用 StreamDiffusion 官方工具安装 TensorRT（自动匹配 CUDA 版本）..."
    cd /root/StreamDiffusion
    python -m streamdiffusion.tools.install-tensorrt 2>&1 | grep -E "Installing|Successfully|Error" | tail -10
    
    # 验证安装
    if python -c "import tensorrt as trt" 2>/dev/null; then
        echo "   ✓ TensorRT 安装成功"
        python -c "import tensorrt as trt; print('   版本:', trt.__version__)"
    else
        echo "   ⚠ TensorRT 安装可能不完整"
    fi
fi
echo ""

# 5. 验证所有依赖
echo "5. 验证依赖..."
python << EOF
import sys
missing = []
try:
    import polygraphy
    print("  ✓ polygraphy")
except ImportError:
    missing.append("polygraphy")
    print("  ✗ polygraphy")

try:
    import onnx_graphsurgeon
    print("  ✓ onnx-graphsurgeon")
except ImportError:
    missing.append("onnx-graphsurgeon")
    print("  ✗ onnx-graphsurgeon")

try:
    import tensorrt as trt
    print(f"  ✓ tensorrt (版本: {trt.__version__})")
except ImportError:
    missing.append("tensorrt")
    print("  ✗ tensorrt")

if missing:
    print(f"\n⚠ 缺少以下依赖: {', '.join(missing)}")
    print("  程序将自动回退到正常模式或使用 xformers")
else:
    print("\n✓ 所有 TensorRT 依赖已安装！")
EOF

echo ""
echo "=========================================="
echo "完成！"
echo "=========================================="

