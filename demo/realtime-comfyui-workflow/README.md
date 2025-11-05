# ComfyUI Workflow - StreamDiffusion Demo

这是一个基于 StreamDiffusion 的实时图像到图像转换演示，实现了 ComfyUI 工作流的参数配置。

## 功能特性

- ✅ 支持 ComfyUI 工作流参数（Checkpoint, LoRA, KSampler 等）
- ✅ 实时图像到图像转换
- ✅ Web 界面支持
- ✅ 可配置的 KSampler 参数（steps, cfg_scale, denoise, seed）
- ✅ 支持 LoRA 加载（strength_model 和 strength_clip）

## 工作流参数

**默认配置（使用 SD-Turbo）**：
- **Checkpoint**: `stabilityai/sd-turbo` (默认，可直接使用)
- **KSampler**: 
  - t_index_list: [35, 45] (SD-Turbo 固定值)
  - cfg_type: "none" (SD-Turbo 不需要 CFG)
  - use_lcm_lora: False (SD-Turbo 不需要 LCM LoRA)

**自定义配置（支持 ComfyUI 工作流参数）**：
- **Checkpoint**: 可以指定本地模型路径或 HuggingFace ID
- **LoRA**: 支持加载 LoRA 文件 (strength_model, strength_clip)
- **KSampler**: 
  - steps: 可配置（非 SD-Turbo 模型）
  - cfg: 可配置（非 SD-Turbo 模型）
  - sampler: lcm (非 SD-Turbo 模型)
  - scheduler: normal
  - denoise: 可配置（非 SD-Turbo 模型）
  - seed: 可配置

## 安装

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 构建前端：

```bash
cd frontend
npm install
npm run build
cd ..
```

## 使用方法

### 方法 1: 使用启动脚本

```bash
chmod +x start.sh
./start.sh
```

### 方法 2: 手动启动（使用 SD-Turbo，默认）

```bash
python main.py \
    --port 6006 \
    --host 0.0.0.0 \
    --model-path "stabilityai/sd-turbo" \
    --acceleration xformers
```

### 方法 3: 使用自定义模型

```bash
python main.py \
    --port 6006 \
    --host 0.0.0.0 \
    --model-path "path/to/your/model.safetensors" \
    --lora-path "path/to/your/lora.safetensors" \
    --lora-strength-model 0.8 \
    --lora-strength-clip 1.0 \
    --acceleration xformers
```

### 环境变量配置

你也可以通过环境变量配置：

```bash
export MODEL_PATH="realisticVisionV60B1_v51HyperVAE.safetensors"
export LORA_PATH="1.5/充气花朵_v1.0.safetensors"
export LORA_STRENGTH_MODEL=0.8
export LORA_STRENGTH_CLIP=1.0
export ACCELERATION=xformers
export PORT=6006

python main.py
```

## 命令行参数

- `--host`: 服务器主机地址（默认: 0.0.0.0）
- `--port`: 服务器端口（默认: 7860）
- `--model-path`: Checkpoint 模型路径
- `--lora-path`: LoRA 文件路径
- `--lora-strength-model`: LoRA 模型强度（UNet）
- `--lora-strength-clip`: LoRA CLIP 强度（Text Encoder）
- `--acceleration`: 加速方式（none, xformers, tensorrt）
- `--engine-dir`: TensorRT 引擎目录
- `--taesd`: 使用 Tiny Autoencoder
- `--safety-checker`: 启用安全检查器
- `--debug`: 调试模式

## Web 界面

启动后，在浏览器中访问：

```
http://localhost:6006
```

界面支持：
- 实时图像输入
- 提示词编辑
- 负面提示词编辑
- KSampler 参数调整（steps, cfg_scale, denoise, seed）

## 注意事项

1. **默认使用 SD-Turbo**: 程序默认使用 `stabilityai/sd-turbo` 模型，这是 HuggingFace 上的公开模型，可以直接下载使用。

2. **SD-Turbo 特殊配置**: 
   - 使用固定的 `t_index_list=[35, 45]`
   - `cfg_type="none"` (不需要 CFG)
   - `use_lcm_lora=False` (不需要 LCM LoRA)
   - 这些配置会自动应用，无需手动设置

3. **自定义模型**: 如果使用其他模型（非 SD-Turbo），程序会自动：
   - 根据 denoise 和 steps 计算 `t_index_list`
   - 使用 LCM LoRA（如果启用）
   - 支持 CFG（根据 cfg_scale 设置）

4. **LoRA strength_clip**: 当前实现中，`lora_dict` 只支持统一的 scale（对应 strength_model）。如果需要分别设置 strength_clip，需要修改代码。

5. **t_index_list 动态修改**: StreamDiffusion 不支持动态修改 `t_index_list`。如果需要修改 steps 或 denoise，需要重新创建 StreamDiffusionWrapper。

6. **模型路径**: 
   - 如果指定本地路径但文件不存在，程序会自动使用默认的 SD-Turbo 模型
   - 程序会在常见路径中查找模型和 LoRA 文件

7. **加速方式**: 
   - `xformers`: **推荐**，兼容性好，通常已安装 ✅
   - `tensorrt`: 最快，但需要安装额外依赖（polygraphy, onnx-graphsurgeon, nvidia-tensorrt）
   - `none`: 不使用加速（最慢）
   
   **注意**: 如果配置了 `tensorrt` 但出现 `ModuleNotFoundError: No module named 'polygraphy'` 错误，说明 TensorRT 未正确安装，程序会自动回退到正常模式（无加速）。此时建议使用 `xformers`。详细说明请参考 `TENSORRT_SETUP.md`。

## 文件结构

```
realtime-comfyui-workflow/
├── config.py              # 配置文件
├── workflow.py            # Pipeline 类（ComfyUI 工作流实现）
├── main.py                # 主程序
├── util.py                # 工具函数
├── connection_manager.py  # WebSocket 连接管理
├── requirements.txt       # Python 依赖
├── start.sh              # 启动脚本
├── frontend/             # 前端代码
└── README.md             # 本文件
```

## 故障排除

### 模型加载失败

- 检查模型路径是否正确
- 确保模型文件存在
- 如果是 HuggingFace ID，确保网络连接正常

### LoRA 加载失败

- 检查 LoRA 文件路径
- 程序会自动在常见路径中查找（models/Lora, models/lora, lora 等）

### 前端构建失败

- 确保已安装 Node.js 和 npm
- 运行 `cd frontend && npm install` 重新安装依赖

## 许可证

与 StreamDiffusion 项目相同。

