# ComfyUI 工作流转 StreamDiffusion 指南

本指南说明如何将 ComfyUI 工作流转换为 StreamDiffusion 代码。

## 工作流参数映射

### 1. Checkpoint 加载器
**ComfyUI**: `CheckpointLoaderSimple`  
**StreamDiffusion**: `model_id_or_path` 参数

```python
model_id_or_path = "realisticVisionV60B1_v51HyperVAE.safetensors"
# 可以是本地路径或 HuggingFace 模型 ID
```

### 2. LoRA 加载器
**ComfyUI**: `LoraLoader` (strength_model, strength_clip)  
**StreamDiffusion**: `lora_dict` 参数

```python
lora_dict = {
    "path/to/lora.safetensors": 0.8  # strength_model
}
# 注意：StreamDiffusion 的 lora_dict 值对应 strength_model
# strength_clip 在 StreamDiffusion 中通过 fuse_lora 的 fuse_text_encoder 控制
```

### 3. VAE
**ComfyUI**: 从 Checkpoint 或单独加载  
**StreamDiffusion**: 
- 如果 checkpoint 已包含 VAE，设置 `use_tiny_vae=False`
- 如果需要单独指定 VAE，使用 `vae_id` 参数

### 4. 图像加载
**ComfyUI**: `LoadImage`  
**StreamDiffusion**: `preprocess_image()` 方法

```python
image_tensor = stream.preprocess_image("input.jpg")
```

### 5. VAE 编码
**ComfyUI**: `VAEEncode`  
**StreamDiffusion**: 自动在 `img2img()` 中处理

### 6. CLIP 文本编码
**ComfyUI**: `CLIPTextEncode` (正面和负面提示词)  
**StreamDiffusion**: `prepare()` 方法

```python
stream.prepare(
    prompt="正面提示词",
    negative_prompt="负面提示词",
    num_inference_steps=50,
    guidance_scale=1.8,
)
```

### 7. KSampler 参数映射

| ComfyUI 参数 | StreamDiffusion 参数 | 说明 |
|-------------|---------------------|------|
| `steps` | `t_index_list` 长度 | 采样步数 |
| `cfg` | `guidance_scale` | CFG 引导强度 |
| `sampler_name` | `use_lcm_lora` | LCM sampler 对应 `use_lcm_lora=True` |
| `scheduler` | 自动使用 LCM Scheduler | StreamDiffusion 默认使用 LCM Scheduler |
| `denoise` | `t_index_list` 计算 | 影响起始噪声索引 |
| `seed` | `seed` | 随机种子 |

#### denoise 参数说明
- `denoise=1.0`: 完全重新生成（从最高噪声开始）
- `denoise=0.6`: 从 60% 的噪声开始（保留 40% 原始图像信息）
- `denoise=0.0`: 几乎不改变（从最低噪声开始）

`t_index_list` 的计算公式：
```python
start_index = int(num_inference_steps * denoise)
# 然后根据 steps 数量均匀分布索引
```

### 8. VAE 解码
**ComfyUI**: `VAEDecode`  
**StreamDiffusion**: 自动在 `img2img()` 中处理

### 9. 图像保存
**ComfyUI**: `SaveImage` 或 `SaveImageWebsocket`  
**StreamDiffusion**: 直接保存 PIL Image

```python
output_image.save("output.png")
```

## 完整示例

参考 `comfyui_workflow_example.py` 文件，其中包含了一个完整的 ComfyUI 工作流转换示例。

### 使用步骤

1. **修改配置参数**：
   - 设置 `MODEL_PATH` 为你的 checkpoint 路径
   - 设置 `LORA_PATH` 为你的 LoRA 文件路径
   - 设置 `INPUT_IMAGE` 为输入图像路径
   - 调整其他参数（提示词、CFG、denoise 等）

2. **运行脚本**：
```bash
python comfyui_workflow_example.py
```

## 参数对应关系总结

### ComfyUI → StreamDiffusion

```python
# Checkpoint
"realisticVisionV60B1_v51HyperVAE.safetensors"
→ model_id_or_path="realisticVisionV60B1_v51HyperVAE.safetensors"

# LoRA
"1.5\充气花朵_v1.0.safetensors" (strength_model=0.8, strength_clip=1.0)
→ lora_dict={"path/to/充气花朵_v1.0.safetensors": 0.8}

# KSampler
steps=4, cfg=1.8, sampler=lcm, denoise=0.6, seed=502923423887318
→ t_index_list=[30, 20, 10, 0]  # 根据 denoise 和 steps 计算
→ guidance_scale=1.8
→ use_lcm_lora=True
→ seed=502923423887318

# 提示词
positive: "masterpiece,inflatable flowers,..."
negative: "ng_deepnegative_v1_75t,..."
→ prompt="masterpiece,inflatable flowers,..."
→ negative_prompt="ng_deepnegative_v1_75t,..."
```

## 注意事项

1. **LoRA strength_clip**: StreamDiffusion 的 `lora_dict` 只接受一个 scale 值（对应 strength_model）。如果需要分别设置 strength_model 和 strength_clip，需要修改 wrapper 或直接使用 `StreamDiffusion` 类。

2. **t_index_list 计算**: denoise 参数会影响 `t_index_list` 的起始索引。建议根据实际效果调整。

3. **VAE**: 如果 checkpoint 名称包含 "VAE" 或 "HyperVAE"，通常已经包含 VAE，设置 `use_tiny_vae=False`。

4. **加速方式**: 
   - `"none"`: 不使用加速
   - `"xformers"`: 使用 xformers（推荐）
   - `"tensorrt"`: 使用 TensorRT（最快，但需要构建引擎）

5. **CFG Type**: 
   - `cfg_type="none"`: 不使用 CFG（guidance_scale <= 1.0）
   - `cfg_type="self"`: RCFG Self-Negative（推荐，计算量 N）
   - `cfg_type="initialize"`: RCFG Onetime-Negative（计算量 N+1）
   - `cfg_type="full"`: 完整 CFG（计算量 2N）

## 常见问题

### Q: 如何精确控制 LoRA 的 strength_clip？
A: 当前 StreamDiffusionWrapper 的限制，`lora_dict` 只支持统一的 scale。如果需要分别设置，可以：
1. 修改 `utils/wrapper.py` 中的 `_load_model` 方法
2. 或直接使用 `StreamDiffusion` 类并手动调用 `load_lora()` 和 `fuse_lora()`

### Q: denoise 参数如何精确映射？
A: denoise 参数影响起始噪声索引。公式为：
```python
start_index = int(num_inference_steps * denoise)
```
然后根据 steps 数量均匀分布索引。如果效果不理想，可以手动调整 `t_index_list`。

### Q: 为什么生成的图像与 ComfyUI 不完全一致？
A: 可能的原因：
1. `t_index_list` 的计算可能不完全匹配
2. LoRA 的 strength_clip 设置可能不同
3. 调度器的实现细节可能略有差异
4. 随机种子的处理方式可能不同

建议通过调整参数来接近 ComfyUI 的效果。

