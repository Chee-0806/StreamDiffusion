#!/bin/bash
# 独立部署脚本
# 将 realtime-comfyui-workflow 部署为独立应用

set -e

# 配置路径（根据实际情况修改）
STREAMDIFFUSION_PATH="${STREAMDIFFUSION_PATH:-$(dirname $(dirname $(pwd)))}"
DEPLOY_PATH="${DEPLOY_PATH:-./realtime-comfyui-standalone}"

echo "=========================================="
echo "StreamDiffusion Realtime Workflow 独立部署"
echo "=========================================="
echo ""
echo "StreamDiffusion 路径: $STREAMDIFFUSION_PATH"
echo "部署路径: $DEPLOY_PATH"
echo ""

# 检查 StreamDiffusion 路径
if [ ! -d "$STREAMDIFFUSION_PATH/src/streamdiffusion" ]; then
    echo "错误: 未找到 StreamDiffusion 源码"
    echo "请设置 STREAMDIFFUSION_PATH 环境变量"
    exit 1
fi

# 创建部署目录
echo "1. 创建部署目录..."
mkdir -p $DEPLOY_PATH
cd $DEPLOY_PATH

# 复制 workflow 文件
echo "2. 复制 workflow 文件..."
cp -r $STREAMDIFFUSION_PATH/demo/realtime-comfyui-workflow/* .
rm -rf __pycache__ 2>/dev/null || true

# 复制 utils 目录
echo "3. 复制 utils 目录..."
cp -r $STREAMDIFFUSION_PATH/utils .

# 创建独立的导入配置
echo "4. 创建独立导入配置..."
cat > workflow_standalone.py << 'EOF'
# 独立部署版本的 workflow.py
# 修改导入路径以支持独立部署

import sys
import os
from pathlib import Path
from typing import Dict, Optional

# 尝试多种导入方式
try:
    # 方式1: utils 在同一目录
    from utils.wrapper import StreamDiffusionWrapper
except ImportError:
    try:
        # 方式2: utils 在上级目录
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from utils.wrapper import StreamDiffusionWrapper
    except ImportError:
        # 方式3: 从环境变量指定的路径导入
        streamdiffusion_path = os.environ.get('STREAMDIFFUSION_PATH')
        if streamdiffusion_path:
            sys.path.insert(0, streamdiffusion_path)
            from utils.wrapper import StreamDiffusionWrapper
        else:
            raise ImportError("无法找到 utils.wrapper，请确保已正确安装 streamdiffusion 包")

# 导入其他模块
import torch
from config import Args
from pydantic import BaseModel, Field
from PIL import Image

# 其余代码从原 workflow.py 复制...
EOF

echo "5. 安装 streamdiffusion 包..."
if [ -d "$STREAMDIFFUSION_PATH" ]; then
    pip install -e $STREAMDIFFUSION_PATH || {
        echo "警告: 无法安装 streamdiffusion，请手动安装:"
        echo "  pip install -e $STREAMDIFFUSION_PATH"
    }
else
    echo "警告: 未找到 StreamDiffusion 路径，请手动安装 streamdiffusion 包"
fi

# 安装依赖
echo "6. 安装依赖..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "警告: 未找到 requirements.txt"
fi

# 构建前端
echo "7. 构建前端..."
if [ -d "frontend" ]; then
    cd frontend
    if [ -f "package.json" ]; then
        npm install
        npm run build
    else
        echo "警告: 未找到 frontend/package.json"
    fi
    cd ..
else
    echo "警告: 未找到 frontend 目录"
fi

# 创建启动脚本
echo "8. 创建启动脚本..."
cat > start_standalone.sh << 'EOF'
#!/bin/bash
# 独立部署启动脚本

# 设置环境变量（如果需要）
export HF_ENDPOINT=${HF_ENDPOINT:-https://hf-mirror.com}
export HF_HUB_ENDPOINT=${HF_HUB_ENDPOINT:-https://hf-mirror.com}

# 启动服务
python main.py \
    --host ${HOST:-0.0.0.0} \
    --port ${PORT:-7860} \
    --model-path ${MODEL_PATH:-stabilityai/sd-turbo} \
    --acceleration ${ACCELERATION:-xformers}
EOF

chmod +x start_standalone.sh

# 创建 README
echo "9. 创建部署说明..."
cat > DEPLOY_README.md << 'EOF'
# 独立部署说明

## 已完成的步骤

1. ✅ 复制了所有必要文件
2. ✅ 安装了 streamdiffusion 包
3. ✅ 安装了依赖
4. ✅ 构建了前端

## 启动服务

```bash
./start_standalone.sh
```

或手动启动：

```bash
python main.py --host 0.0.0.0 --port 7860
```

## 环境变量

- `HOST`: 服务地址（默认: 0.0.0.0）
- `PORT`: 服务端口（默认: 7860）
- `MODEL_PATH`: 模型路径（默认: stabilityai/sd-turbo）
- `ACCELERATION`: 加速方式（默认: xformers）
- `HF_ENDPOINT`: HuggingFace 镜像（默认: https://hf-mirror.com）

## 注意事项

1. 确保已安装 CUDA 和 PyTorch
2. 确保有足够的 GPU 内存
3. 首次运行会下载模型，需要网络连接

## 依赖检查

运行以下命令检查依赖：

```bash
python -c "from streamdiffusion import StreamDiffusion; print('✓ StreamDiffusion')"
python -c "from utils.wrapper import StreamDiffusionWrapper; print('✓ Wrapper')"
python -c "import fastapi; print('✓ FastAPI')"
```
EOF

echo ""
echo "=========================================="
echo "部署完成！"
echo "=========================================="
echo ""
echo "部署路径: $(pwd)"
echo ""
echo "下一步："
echo "1. 检查依赖: python -c 'from streamdiffusion import StreamDiffusion'"
echo "2. 启动服务: ./start_standalone.sh"
echo "3. 访问: http://localhost:7860"
echo ""
echo "详细说明请查看 DEPLOY_README.md"

