# 动态 LoRA 切换实现说明

## 功能概述

已实现运行时动态切换 LoRA 功能，无需重启服务即可切换不同的 LoRA 模型。

## 实现原理

### 核心思路

1. **不使用 fuse_lora()**: 
   - 传统方式使用 `fuse_lora()` 将 LoRA 融合到模型中，融合后无法动态切换
   - 新实现直接使用 `load_lora_weights()` 加载，不融合，支持 `unload_lora_weights()` 卸载

2. **动态加载/卸载**:
   - 使用 diffusers 的 `load_lora_weights()` 和 `unload_lora_weights()` API
   - 在切换时先卸载当前 LoRA，再加载新的 LoRA

3. **自动检测切换请求**:
   - 在 `predict()` 方法中检测 `lora_selection` 参数变化
   - 自动触发 LoRA 切换

## 代码实现

### 1. 初始化时不融合 LoRA

```python
# 在 __init__ 中，不通过 wrapper 传递 lora_dict
# 而是在 prepare() 之后单独加载
self.stream = StreamDiffusionWrapper(
    model_id_or_path=model_path_str,
    lora_dict=None,  # 不在这里加载，避免融合
    ...
)

# prepare 之后加载初始 LoRA
if initial_lora_path:
    self.stream.stream.pipe.load_lora_weights(initial_lora_path)
    # 注意：不调用 fuse_lora()
```

### 2. 动态切换方法

```python
def switch_lora(self, lora_selection: str) -> bool:
    """动态切换 LoRA"""
    # 1. 查找预设
    # 2. 卸载当前 LoRA
    if self.current_lora:
        self._unload_lora()
    # 3. 加载新 LoRA
    self._load_lora(lora_path, lora_strength)
```

### 3. 自动检测切换

```python
def predict(self, params: "Pipeline.InputParams") -> Image.Image:
    # 检测 LoRA 切换请求
    if hasattr(params, 'lora_selection') and params.lora_selection:
        if params.lora_selection != getattr(self, '_last_lora_selection', 'none'):
            self.switch_lora(params.lora_selection)
```

## 使用方法

### 前端操作

1. 在页面上选择不同的 LoRA 预设
2. 系统会自动检测变化并切换
3. 切换过程会在控制台输出日志

### 后端 API

切换通过前端参数自动触发，无需单独的 API 接口。

## 性能考虑

### 优点

- ✅ 无需重启服务
- ✅ 快速切换（几秒内完成）
- ✅ 支持多个 LoRA 预设

### 缺点

- ⚠️ 未融合的 LoRA 可能影响性能（每次推理都需要应用 LoRA）
- ⚠️ 首次加载 LoRA 需要下载（如果从 HuggingFace）
- ⚠️ 切换时可能短暂影响推理速度

### 性能优化建议

1. **预加载常用 LoRA**: 可以在启动时预加载多个 LoRA
2. **使用本地 LoRA**: 避免每次切换时下载
3. **缓存 LoRA 权重**: diffusers 会自动缓存下载的模型

## 兼容性

### 支持的情况

- ✅ 未融合的 LoRA（新加载方式）
- ✅ 支持 HuggingFace ID 和本地路径
- ✅ 自动检测 HuggingFace ID vs 本地路径

### 不支持的情况

- ❌ 已融合的 LoRA（如果初始化失败回退到融合模式）
- ❌ 某些旧版本的 diffusers（可能不支持 `unload_lora_weights`）

### 回退机制

如果直接加载失败，系统会自动回退到融合模式：
- 加载 LoRA 并融合
- 标记为已融合，无法动态切换
- 提示用户需要重启服务才能切换

## 故障排查

### 问题：切换失败

1. **检查日志**: 查看控制台输出的错误信息
2. **检查 LoRA 路径**: 确认 LoRA 文件存在或 HuggingFace ID 正确
3. **检查网络**: 如果使用 HuggingFace，确保网络连接正常

### 问题：切换后没有效果

1. **检查是否已融合**: 查看日志中是否有 "已融合" 提示
2. **检查 LoRA 兼容性**: 确保 LoRA 与基础模型兼容
3. **检查 LoRA 强度**: 某些 LoRA 可能需要特定的强度值

### 问题：性能下降

1. **正常现象**: 未融合的 LoRA 会影响性能
2. **解决方案**: 
   - 如果性能问题严重，可以重启服务并融合 LoRA
   - 或者使用更强大的 GPU

## 未来改进

1. **支持多个 LoRA 同时加载**: 使用 adapter 系统
2. **LoRA 强度调整**: 支持运行时调整 LoRA 强度
3. **LoRA 预热**: 预加载常用 LoRA 以加快切换速度
4. **性能监控**: 添加性能指标，帮助用户选择合适的模式

