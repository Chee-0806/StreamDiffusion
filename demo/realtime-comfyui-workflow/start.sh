#!/bin/bash
# 使用 bash 而不是 sh，确保 source 命令可用
# 使用数据盘存储 pip 缓存和临时文件，避免占用系统盘
export PIP_CACHE_DIR=/root/autodl-tmp/.cache/pip
export TMPDIR=/root/autodl-tmp/tmp
export TMP=/root/autodl-tmp/tmp
export TEMP=/root/autodl-tmp/tmp

# 设置 Hugging Face 模型缓存目录到数据盘
export HF_HOME=/root/autodl-tmp/.cache/huggingface
export HUGGINGFACE_HUB_CACHE=/root/autodl-tmp/.cache/huggingface

# 设置 CUDA 和 TensorRT 环境变量（修复 CUDA 初始化错误 35）
if [ -d "/usr/local/cuda-12" ]; then
    export CUDA_HOME=/usr/local/cuda-12
    export PATH=/usr/local/cuda-12/bin:$PATH
    export LD_LIBRARY_PATH=/usr/local/cuda-12/lib64:$LD_LIBRARY_PATH
elif [ -d "/usr/local/cuda" ]; then
    export CUDA_HOME=/usr/local/cuda
    export PATH=/usr/local/cuda/bin:$PATH
    export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
fi

# 添加 TensorRT 库路径到 LD_LIBRARY_PATH（关键！）
TRT_LIB_PATH="/root/autodl-tmp/venv/lib/python3.10/site-packages/tensorrt_libs"
if [ -d "$TRT_LIB_PATH" ]; then
    export LD_LIBRARY_PATH=$TRT_LIB_PATH:$LD_LIBRARY_PATH
    echo "TensorRT 库路径已添加到 LD_LIBRARY_PATH: $TRT_LIB_PATH"
fi

# 设置 CUDA 模块加载模式（可能有助于解决 CUDA 初始化问题）
export CUDA_MODULE_LOADING=LAZY

export POLYGRAPHY_AUTOINSTALL_DEPS=1

cd frontend
npm install
npm run build
if [ $? -eq 0 ]; then
    echo -e "\033[1;32m\nfrontend build success \033[0m"
else
    echo -e "\033[1;31m\nfrontend build failed\n\033[0m" >&2
    exit 1
fi
cd ../
# 激活虚拟环境并使用正确的 Python
source /root/autodl-tmp/venv/bin/activate

# 确保使用修改后的源代码（开发模式）
export PYTHONPATH=/root/StreamDiffusion/src:$PYTHONPATH

# 性能优化：单步模式（最快）或双步模式（默认，平衡质量和速度）
# 设置 TURBO_STEPS=1 启用单步模式（最快速度，~94 fps）
# 设置 TURBO_STEPS=2 或省略使用双步模式（默认，质量更好，~50-60 fps）
export TURBO_STEPS=${TURBO_STEPS:-2}

python3 main.py --port 6006 --host 0.0.0.0 \
    --model-path "stabilityai/sd-turbo" \
    --acceleration tensorrt
# 注意：TensorRT 需要正确的库路径配置
# 已自动设置 TensorRT 库路径到 LD_LIBRARY_PATH
# 如果仍然遇到 CUDA 初始化错误，可能需要：
# 1. 检查 CUDA 驱动版本兼容性
# 2. 或使用 xformers 作为替代：--acceleration xformers
# 如果需要使用本地模型，取消下面的注释并修改路径：
# --model-path "path/to/your/model.safetensors" \
# --lora-path "path/to/your/lora.safetensors" \
# --lora-strength-model 0.8 \
# --lora-strength-clip 1.0

