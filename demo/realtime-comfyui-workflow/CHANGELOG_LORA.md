# LoRA HuggingFace 支持更新日志

## 更新内容

### ✅ 已完成功能

1. **HuggingFace LoRA 支持**
   - ✅ 自动识别 HuggingFace ID 和本地路径
   - ✅ 使用国内镜像站 (hf-mirror.com) 自动下载
   - ✅ 支持 HuggingFace ID 格式：`author/model-name`

2. **LoRA 预设列表**
   - ✅ 添加了 6 个预设 LoRA 选项
   - ✅ 支持通过 API 获取预设列表
   - ✅ 每个预设包含：ID、名称、路径、强度、描述

3. **后端 API 接口**
   - ✅ 新增 `/api/lora-presets` 接口
   - ✅ 返回所有可用预设列表
   - ✅ 显示当前使用的 LoRA 和镜像信息

4. **前端参数**
   - ✅ 在 `InputParams` 中添加 `lora_selection` 字段
   - ✅ 支持前端选择 LoRA 预设（注意：实际切换需要重新启动服务）

## 使用方法

### 1. 通过命令行使用 HuggingFace LoRA

```bash
# 使用 HuggingFace ID
python3 main.py \
    --lora-path "author/model-name" \
    --lora-strength-model 0.8

# 使用本地文件
python3 main.py \
    --lora-path "models/LoRA/your_lora.safetensors" \
    --lora-strength-model 0.8
```

### 2. 通过环境变量

```bash
export LORA_PATH="author/model-name"
export LORA_STRENGTH_MODEL=0.8
python3 main.py
```

### 3. 通过 API 获取预设列表

```bash
curl http://localhost:7860/api/lora-presets
```

**响应示例**:
```json
{
  "presets": [
    {
      "id": "none",
      "name": "无 LoRA",
      "path": null,
      "strength_model": 0.0,
      "description": "不使用任何 LoRA"
    },
    {
      "id": "anime_style",
      "name": "动漫风格",
      "path": "ostris/super-cereal-sdxl-lora",
      "strength_model": 0.8,
      "description": "动漫风格 LoRA"
    },
    ...
  ],
  "current_lora": null,
  "mirror_info": "使用 HuggingFace 国内镜像 (hf-mirror.com) 自动下载"
}
```

## 预设 LoRA 列表

| ID | 名称 | HuggingFace 路径 | 强度 | 说明 |
|---|---|---|---|---|
| `none` | 无 LoRA | - | 0.0 | 不使用任何 LoRA |
| `anime_style` | 动漫风格 | `ostris/super-cereal-sdxl-lora` | 0.8 | 动漫风格 LoRA |
| `realistic_vision` | 写实风格 | `sayakpaul/sd-model-finetuned-lora-t2i` | 0.7 | 写实风格 LoRA |
| `chinese_style` | 中国风 | `Linaqruf/anything-v3.0` | 0.8 | 中国风风格 LoRA |
| `watercolor` | 水彩风格 | `ostris/watercolor_style_lora` | 0.75 | 水彩画风格 LoRA |
| `oil_painting` | 油画风格 | `ostris/oil_painting_style_lora` | 0.7 | 油画风格 LoRA |

## 技术实现

### 自动识别机制

系统会自动判断 LoRA 路径类型：

**HuggingFace ID 识别条件**:
- 包含 `/` 字符
- 不以 `.safetensors/.ckpt/.pt/.pth` 结尾
- 不是绝对路径
- 文件不存在

**本地路径识别条件**:
- 绝对路径或相对路径
- 以 `.safetensors/.ckpt/.pt/.pth` 结尾
- 文件存在

### 镜像配置

国内镜像已在 `utils/wrapper.py` 中配置：
```python
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["HF_HUB_ENDPOINT"] = "https://hf-mirror.com"
```

### 代码修改位置

1. **workflow.py**:
   - 添加 `LORA_PRESETS` 预设列表
   - 修改 LoRA 加载逻辑，支持 HuggingFace ID
   - 添加 `lora_selection` 字段到 `InputParams`

2. **main.py**:
   - 添加 `/api/lora-presets` API 接口

## 注意事项

1. **首次下载**: LoRA 模型首次使用时会自动下载，需要网络连接
2. **模型兼容性**: 确保 LoRA 与基础模型（如 SD-Turbo）兼容
3. **动态切换**: LoRA 在初始化时加载，无法运行时动态切换（需要重启服务）
4. **缓存位置**: 下载的模型会缓存在 `~/.cache/huggingface/` 或 `HF_HOME` 环境变量指定的目录

## 后续改进建议

1. 支持运行时动态切换 LoRA（需要重新初始化 pipeline）
2. 支持同时加载多个 LoRA
3. 添加 LoRA 预览功能
4. 支持从 Civitai 等其他平台下载

## 相关文档

- `LORA_HUGGINGFACE_SETUP.md` - 详细配置指南
- `LORA_GUIDE.md` - LoRA 使用指南（包含训练方法）

