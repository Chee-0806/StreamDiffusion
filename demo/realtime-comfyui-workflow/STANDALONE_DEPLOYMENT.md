# 独立部署指南

## 概述

`realtime-comfyui-workflow` 可以独立部署，但需要 StreamDiffusion 的核心包。有两种部署方式：

## 方案一：作为 StreamDiffusion 的依赖（推荐）

### 优点
- ✅ 简单，只需安装 streamdiffusion 包
- ✅ 自动处理依赖关系
- ✅ 易于更新和维护

### 步骤

1. **安装 StreamDiffusion 包**
   ```bash
   # 从源码安装
   cd /path/to/StreamDiffusion
   pip install -e .
   
   # 或从 PyPI 安装（如果有）
   pip install streamdiffusion
   ```

2. **复制 workflow 目录**
   ```bash
   cp -r /path/to/StreamDiffusion/demo/realtime-comfyui-workflow /your/deploy/path/
   ```

3. **复制 utils 目录（包含 wrapper）**
   ```bash
   cp -r /path/to/StreamDiffusion/utils /your/deploy/path/
   ```

4. **修改导入路径**
   
   修改 `workflow.py` 中的导入：
   ```python
   # 原代码
   sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
   from utils.wrapper import StreamDiffusionWrapper
   
   # 改为（如果 utils 在同一目录）
   from utils.wrapper import StreamDiffusionWrapper
   
   # 或（如果 utils 在上级目录）
   sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
   from utils.wrapper import StreamDiffusionWrapper
   ```

5. **安装依赖**
   ```bash
   cd /your/deploy/path/realtime-comfyui-workflow
   pip install -r requirements.txt
   ```

## 方案二：完全独立部署（需要更多工作）

### 优点
- ✅ 完全独立，不依赖 StreamDiffusion 项目结构
- ✅ 可以自定义和优化

### 缺点
- ⚠️ 需要复制更多代码
- ⚠️ 需要手动管理依赖

### 步骤

1. **创建独立项目目录**
   ```bash
   mkdir -p realtime-comfyui-standalone
   cd realtime-comfyui-standalone
   ```

2. **复制必要文件**
   ```bash
   # 复制 workflow 文件
   cp -r /path/to/StreamDiffusion/demo/realtime-comfyui-workflow/* .
   
   # 复制 utils 目录
   cp -r /path/to/StreamDiffusion/utils .
   
   # 复制 streamdiffusion 源码（或安装包）
   # 选项 A: 安装为依赖
   pip install -e /path/to/StreamDiffusion
   
   # 选项 B: 复制源码
   mkdir -p src
   cp -r /path/to/StreamDiffusion/src/streamdiffusion src/
   ```

3. **修改导入路径**

   修改 `workflow.py`:
   ```python
   # 如果 streamdiffusion 已安装，直接导入
   from streamdiffusion import StreamDiffusion
   from streamdiffusion.image_utils import postprocess_image
   
   # 如果复制了源码，添加到路径
   import sys
   sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
   from streamdiffusion import StreamDiffusion
   ```

4. **创建独立的 requirements.txt**

   创建 `requirements.txt`:
   ```txt
   # StreamDiffusion 核心依赖
   torch
   diffusers==0.24.0
   transformers==4.35.2
   accelerate==0.24.0
   numpy<2.0
   Pillow==10.1.0
   
   # Web framework
   fastapi==0.104.1
   uvicorn[standard]==0.24.0.post1
   pydantic
   
   # LoRA 支持
   peft==0.6.0
   compel==2.0.2
   
   # Hugging Face
   huggingface_hub<0.20.0
   
   # Utilities
   markdown2
   
   # Acceleration
   xformers
   ```

5. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

## 方案三：Docker 部署（最推荐）

### 创建 Dockerfile

```dockerfile
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04

WORKDIR /app

# 安装 Python
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安装 StreamDiffusion
RUN pip install --no-cache-dir streamdiffusion

# 复制应用代码
COPY realtime-comfyui-workflow/ /app/
COPY utils/ /app/utils/

# 安装应用依赖
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# 构建前端
WORKDIR /app/frontend
RUN npm install && npm run build

# 暴露端口
EXPOSE 7860

# 启动命令
WORKDIR /app
CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "7860"]
```

### 构建和运行

```bash
docker build -t realtime-comfyui:latest .
docker run --gpus all -p 7860:7860 realtime-comfyui:latest
```

## 最小依赖检查清单

### 必需的 StreamDiffusion 组件

1. **核心包**: `streamdiffusion` (可通过 pip 安装)
   - `StreamDiffusion` 类
   - `image_utils` 模块

2. **Wrapper**: `utils/wrapper.py`
   - `StreamDiffusionWrapper` 类
   - 依赖 `streamdiffusion` 包

3. **加速支持** (可选):
   - `streamdiffusion.acceleration.tensorrt`
   - `streamdiffusion.acceleration.sfast`

### 必需的外部依赖

- PyTorch (CUDA 版本)
- diffusers==0.24.0
- transformers==4.35.2
- FastAPI + Uvicorn
- 其他见 `requirements.txt`

## 快速独立部署脚本

创建 `deploy_standalone.sh`:

```bash
#!/bin/bash
set -e

# 配置
STREAMDIFFUSION_PATH="/path/to/StreamDiffusion"
DEPLOY_PATH="./realtime-comfyui-standalone"

# 创建目录
mkdir -p $DEPLOY_PATH
cd $DEPLOY_PATH

# 复制文件
echo "复制 workflow 文件..."
cp -r $STREAMDIFFUSION_PATH/demo/realtime-comfyui-workflow/* .

# 复制 utils
echo "复制 utils..."
cp -r $STREAMDIFFUSION_PATH/utils .

# 安装 streamdiffusion
echo "安装 streamdiffusion..."
pip install -e $STREAMDIFFUSION_PATH

# 安装依赖
echo "安装依赖..."
pip install -r requirements.txt

# 构建前端
echo "构建前端..."
cd frontend
npm install
npm run build
cd ..

echo "部署完成！"
echo "运行: python main.py"
```

## 验证部署

运行以下命令验证：

```bash
python -c "from streamdiffusion import StreamDiffusion; print('✓ StreamDiffusion 可用')"
python -c "from utils.wrapper import StreamDiffusionWrapper; print('✓ Wrapper 可用')"
python -c "import fastapi; print('✓ FastAPI 可用')"
```

## 常见问题

### Q: 必须安装整个 StreamDiffusion 项目吗？

A: 不需要整个项目，但需要：
- `streamdiffusion` Python 包（可通过 pip 安装）
- `utils/wrapper.py` 文件

### Q: 可以只复制需要的文件吗？

A: 可以，但需要：
1. 安装 `streamdiffusion` 包（包含核心逻辑）
2. 复制 `utils/wrapper.py`
3. 确保所有依赖已安装

### Q: 如何最小化部署体积？

A: 
1. 只安装必要的依赖
2. 使用 Docker 多阶段构建
3. 不包含 TensorRT（如果不需要）

### Q: 前端必须构建吗？

A: 是的，前端需要构建。可以：
- 在部署前构建：`cd frontend && npm run build`
- 或在 Docker 中构建

## 总结

**推荐方案**：
1. 安装 `streamdiffusion` 包（`pip install -e .`）
2. 复制 `realtime-comfyui-workflow` 目录
3. 复制 `utils` 目录
4. 安装依赖并运行

这样既保持了独立性，又避免了重复代码。

