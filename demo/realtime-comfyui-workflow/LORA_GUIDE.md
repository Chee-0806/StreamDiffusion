# LoRA 使用指南

## 1. 下载现成的 LoRA

### 推荐网站
- **Civitai**: https://civitai.com（需科学上网）
- **Hugging Face**: https://huggingface.co/models?pipeline_tag=text-to-image&library=lora
- **LiblibAI**: https://www.liblib.ai（国内可访问）

### 放置位置
将下载的 `.safetensors` 文件放到以下任一目录：
- `/root/StreamDiffusion/models/LoRA/`（推荐）
- `/root/StreamDiffusion/models/lora/`
- `/root/StreamDiffusion/lora/`

## 2. 使用 LoRA

### 方法一：命令行参数
```bash
python3 main.py \
    --lora-path "models/LoRA/你的LoRA文件名.safetensors" \
    --lora-strength-model 0.8 \
    --lora-strength-clip 1.0
```

### 方法二：环境变量
```bash
export LORA_PATH="models/LoRA/你的LoRA文件名.safetensors"
export LORA_STRENGTH_MODEL=0.8
export LORA_STRENGTH_CLIP=1.0
python3 main.py
```

### 参数说明
- `--lora-path`: LoRA 文件路径（相对于项目根目录或绝对路径）
- `--lora-strength-model`: UNet 的 LoRA 强度（0.0-2.0，推荐 0.6-1.0）
- `--lora-strength-clip`: CLIP 文本编码器的 LoRA 强度（通常 1.0）

## 3. 训练自己的 LoRA

### 使用 Kohya_ss（推荐）

1. **安装 Kohya_ss**
   ```bash
   git clone https://github.com/bmaltais/kohya_ss
   cd kohya_ss
   ./setup.sh
   ```

2. **准备训练数据**
   - 收集 20-100 张高质量图片（同一主题/风格）
   - 为每张图片准备对应的提示词（caption）
   - 建议图片分辨率：512x512 或 768x768

3. **配置训练参数**
   - 使用 GUI 界面或配置文件
   - 基础模型：选择与 StreamDiffusion 兼容的模型（如 SD 1.5）
   - 训练步数：通常 1000-2000 步
   - 学习率：1e-4 到 1e-3

4. **开始训练**
   ```bash
   python train_network.py --config_file config.json
   ```

5. **导出 LoRA**
   - 训练完成后，在 `output` 目录找到 `.safetensors` 文件
   - 复制到 `/root/StreamDiffusion/models/LoRA/`

### 使用 ComfyUI 训练

1. 安装 ComfyUI 的 LoRA 训练节点
2. 通过工作流界面配置训练参数
3. 导出训练好的 LoRA 文件

### 使用 Stable Diffusion WebUI

1. 安装 WebUI 的 LoRA 训练扩展（如 Additional Networks）
2. 在训练标签页配置参数
3. 导出 `.safetensors` 文件

## 4. 常见问题

### Q: LoRA 强度设置多少合适？
- **模型强度（strength_model）**: 
  - 0.6-0.8：轻微效果，保持原图风格
  - 0.8-1.0：标准效果（推荐）
  - 1.0-1.5：强烈效果，可能过度风格化
- **CLIP 强度（strength_clip）**: 通常保持 1.0

### Q: 找不到 LoRA 文件？
- 检查文件路径是否正确
- 确认文件名完整（包括 `.safetensors` 扩展名）
- 检查文件权限（确保可读）

### Q: LoRA 效果不明显？
- 尝试提高 `lora-strength-model` 值（最高 2.0）
- 检查提示词是否包含 LoRA 的触发词
- 确认 LoRA 与基础模型兼容（SD 1.5 vs SDXL）

### Q: 可以同时使用多个 LoRA 吗？
- 当前代码支持，修改 `lora_dict` 为多个条目：
  ```python
  lora_dict = {
      "path/to/lora1.safetensors": 0.8,
      "path/to/lora2.safetensors": 0.6,
  }
  ```

## 5. 推荐 LoRA 资源

### 风格类
- 动漫风格
- 写实风格
- 油画风格
- 水彩风格

### 角色类
- 特定角色
- 服装风格
- 发型风格

### 概念类
- 建筑风格
- 科幻风格
- 奇幻风格

## 6. 训练数据准备建议

1. **图片质量**
   - 分辨率：512x512 或更高
   - 清晰、无模糊
   - 主题突出

2. **图片数量**
   - 最少：20 张
   - 推荐：50-100 张
   - 过多可能导致过拟合

3. **标注质量**
   - 准确描述图片内容
   - 包含关键特征词
   - 避免冗余描述

4. **数据增强**
   - 可以适当使用翻转、裁剪
   - 保持风格一致性

