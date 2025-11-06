# HuggingFace LoRA 配置指南

## 功能说明

现在系统支持从 HuggingFace Hub 自动下载 LoRA 模型，并使用国内镜像加速下载。

## 国内镜像配置

系统已自动配置使用 HuggingFace 国内镜像站：
- **镜像地址**: https://hf-mirror.com
- **自动配置**: 在 `utils/wrapper.py` 中已设置环境变量

## 使用方法

### 方法一：通过命令行参数

```bash
# 使用 HuggingFace LoRA ID
python3 main.py \
    --lora-path "author/model-name" \
    --lora-strength-model 0.8

# 使用本地 LoRA 文件
python3 main.py \
    --lora-path "models/LoRA/your_lora.safetensors" \
    --lora-strength-model 0.8
```

### 方法二：通过环境变量

```bash
export LORA_PATH="author/model-name"
export LORA_STRENGTH_MODEL=0.8
python3 main.py
```

### 方法三：修改 start.sh

在 `start.sh` 中添加参数：

```bash
python3 main.py --port 6006 --host 0.0.0.0 \
    --model-path "stabilityai/sd-turbo" \
    --lora-path "author/model-name" \
    --lora-strength-model 0.8 \
    --acceleration tensorrt
```

## API 接口

### 获取 LoRA 预设列表

```bash
GET /api/lora-presets
```

**响应示例**:
```json
{
  "presets": [
    {
      "id": "anime_style",
      "name": "动漫风格",
      "path": "ostris/super-cereal-sdxl-lora",
      "strength_model": 0.8,
      "description": "动漫风格 LoRA"
    },
    ...
  ],
  "current_lora": "author/model-name",
  "mirror_info": "使用 HuggingFace 国内镜像 (hf-mirror.com) 自动下载"
}
```

## 自动识别机制

系统会自动识别 LoRA 路径类型：

1. **HuggingFace ID**: 
   - 格式：`author/model-name`
   - 包含 `/` 但不以 `.safetensors/.ckpt/.pt/.pth` 结尾
   - 不是绝对路径且文件不存在
   - **示例**: `ostris/super-cereal-sdxl-lora`

2. **本地路径**:
   - 绝对路径或相对路径
   - 以 `.safetensors/.ckpt/.pt/.pth` 结尾
   - 文件存在
   - **示例**: `models/LoRA/my_lora.safetensors`

## 查找 HuggingFace LoRA

### 推荐网站

1. **HuggingFace Hub**: https://huggingface.co/models?pipeline_tag=text-to-image&library=lora
   - 使用国内镜像访问: https://hf-mirror.com/models?pipeline_tag=text-to-image&library=lora

2. **Civitai**: https://civitai.com
   - 很多 LoRA 也会上传到 HuggingFace

3. **搜索技巧**:
   - 在 HuggingFace Hub 搜索 "lora stable-diffusion"
   - 查看模型的 README 确认兼容性
   - 注意模型对应的基础模型（SD 1.5 或 SDXL）

## 预设 LoRA 列表

系统内置了多个预设选项，可通过 `/api/lora-presets` 接口查看。

### 添加自定义预设

编辑 `workflow.py` 中的 `LORA_PRESETS` 列表：

```python
LORA_PRESETS = [
    {
        "id": "your_custom_lora",
        "name": "你的 LoRA 名称",
        "path": "author/model-name",  # 或本地路径 "models/LoRA/file.safetensors"
        "strength_model": 0.8,
        "description": "描述信息"
    },
    ...
]
```

## 常见问题

### Q: 如何确认 LoRA 是否下载成功？

查看启动日志，应该会看到：
```
使用 HuggingFace LoRA: author/model-name (强度: 0.8)
```

### Q: 下载速度慢怎么办？

- 系统已配置使用国内镜像 (hf-mirror.com)
- 如果仍然慢，可以手动下载模型到本地，然后使用本地路径

### Q: LoRA 不兼容怎么办？

- 确保 LoRA 与基础模型兼容（SD 1.5 vs SDXL）
- 检查 LoRA 的 README 文档
- 尝试调整 `lora-strength-model` 参数

### Q: 如何同时使用多个 LoRA？

当前版本支持在 `lora_dict` 中指定多个 LoRA，但需要在代码中手动配置。
未来版本可能会支持通过 API 动态添加多个 LoRA。

### Q: 模型下载失败？

- 检查网络连接
- 确认模型 ID 正确
- 查看 HuggingFace Hub 上模型是否存在
- 尝试使用本地路径

## 性能优化

1. **首次下载**: LoRA 模型会缓存在本地，后续启动会直接使用缓存
2. **缓存位置**: 默认在 `~/.cache/huggingface/` 或环境变量 `HF_HOME` 指定的目录
3. **离线使用**: 下载后可以离线使用，无需每次下载

## 注意事项

1. **模型兼容性**: 确保 LoRA 与基础模型（如 SD-Turbo）兼容
2. **首次下载**: 首次使用某个 LoRA 时需要下载，可能需要一些时间
3. **磁盘空间**: LoRA 模型通常几十到几百 MB，确保有足够空间
4. **网络要求**: 虽然使用国内镜像，但仍需要网络连接进行首次下载

