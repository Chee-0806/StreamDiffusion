# ComfyUI → StreamDiffusion 快速参考

## 你的工作流参数映射

根据你提供的 ComfyUI 工作流，以下是参数映射：

### 配置参数

```python
# 模型
MODEL_PATH = "realisticVisionV60B1_v51HyperVAE.safetensors"

# LoRA
LORA_PATH = r"1.5\充气花朵_v1.0.safetensors"
LORA_STRENGTH_MODEL = 0.8
LORA_STRENGTH_CLIP = 1.0  # 注意：StreamDiffusion 中需要特殊处理

# 输入图像
INPUT_IMAGE = "86d4a0913d90aa71c0377f0b980c6274.jpg"

# KSampler 参数
STEPS = 4
CFG_SCALE = 1.8
DENOISE_STRENGTH = 0.6
SEED = 502923423887318

# 提示词
PROMPT = "masterpiece,inflatable flowers,transparency,blue sky background,high quality,"
NEGATIVE_PROMPT = "ng_deepnegative_v1_75t,(badhandv4:1.2),EasyNegative,(worst quality:2),balloon,,nsfw"
```

### 关键映射

| ComfyUI | StreamDiffusion | 值 |
|---------|----------------|-----|
| CheckpointLoaderSimple | `model_id_or_path` | `"realisticVisionV60B1_v51HyperVAE.safetensors"` |
| LoraLoader (strength_model) | `lora_dict` 值 | `0.8` |
| LoraLoader (strength_clip) | `fuse_lora(fuse_text_encoder=True)` | `1.0` (需要手动设置) |
| KSampler (steps) | `t_index_list` 长度 | `4` → `[30, 20, 10, 0]` |
| KSampler (cfg) | `guidance_scale` | `1.8` |
| KSampler (sampler=lcm) | `use_lcm_lora` | `True` |
| KSampler (denoise) | `t_index_list` 起始索引 | `0.6` → 从索引 30 开始 |
| KSampler (seed) | `seed` | `502923423887318` |

### 代码示例

```python
from utils.wrapper import StreamDiffusionWrapper

# 初始化
stream = StreamDiffusionWrapper(
    model_id_or_path="realisticVisionV60B1_v51HyperVAE.safetensors",
    lora_dict={"path/to/充气花朵_v1.0.safetensors": 0.8},
    t_index_list=[30, 20, 10, 0],  # denoise=0.6, steps=4
    frame_buffer_size=1,
    width=512,
    height=512,
    warmup=10,
    acceleration="xformers",
    mode="img2img",
    use_denoising_batch=True,
    cfg_type="self",  # CFG > 1.0 时使用 RCFG
    seed=502923423887318,
    use_lcm_lora=True,
    use_tiny_vae=False,  # checkpoint 已包含 VAE
)

# 准备
stream.prepare(
    prompt="masterpiece,inflatable flowers,transparency,blue sky background,high quality,",
    negative_prompt="ng_deepnegative_v1_75t,(badhandv4:1.2),EasyNegative,(worst quality:2),balloon,,nsfw",
    num_inference_steps=50,
    guidance_scale=1.8,
)

# 处理图像
image_tensor = stream.preprocess_image("86d4a0913d90aa71c0377f0b980c6274.jpg")

# 预热
for _ in range(stream.batch_size - 1):
    stream(image=image_tensor)

# 生成
output_image = stream(image=image_tensor)
output_image.save("output.png")
```

## 运行完整示例

```bash
# 1. 修改 comfyui_workflow_example.py 中的路径
# 2. 运行
python comfyui_workflow_example.py
```

## 常见问题

**Q: t_index_list 如何计算？**  
A: 使用 `calculate_t_index_list(steps, denoise)` 函数自动计算。

**Q: LoRA 的 strength_clip 如何设置？**  
A: 当前 StreamDiffusionWrapper 限制，`lora_dict` 只支持统一的 scale。如果需要分别设置，需要修改 wrapper 或直接使用 StreamDiffusion 类。

**Q: 为什么结果与 ComfyUI 不完全一致？**  
A: 可能原因：
- `t_index_list` 的计算可能不完全匹配
- LoRA strength_clip 设置可能不同
- 调度器实现细节差异

建议通过调整参数来接近 ComfyUI 的效果。

