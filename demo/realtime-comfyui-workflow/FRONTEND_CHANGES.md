# 前端修改说明

## 已完成的修改

### 1. LoRA 选择器功能

#### 新增组件
- **LoraSelector.svelte**: 专门用于选择 LoRA 预设的组件
  - 自动从 `/api/lora-presets` 获取预设列表
  - 显示 LoRA 名称、路径和描述
  - 支持显示当前使用的自定义 LoRA

#### 集成到 PipelineOptions
- 在 `PipelineOptions.svelte` 中集成了 LoRA 选择器
- 当检测到 `lora_selection` 字段时，使用专门的 LoRA 选择器组件
- 其他字段继续使用原有组件

### 2. 中文界面

#### 页面文字中文化
- **主页面 (+page.svelte)**:
  - "Loading..." → "加载中..."
  - "Start" → "开始"
  - "Stop" → "停止"
  - "Session timed out. Please try again." → "会话超时，请重试。"
  - 队列信息提示改为中文

- **PipelineOptions.svelte**:
  - "Advanced Options" → "高级选项"

- **TextArea.svelte**:
  - "Add your prompt here..." → "在此输入提示词..."

- **workflow.py**:
  - 页面内容 (`page_content`) 改为中文
  - LoRA 选择器字段标题和描述已为中文

### 3. 后端 API 支持

- `/api/lora-presets` 接口已实现，返回：
  - 预设列表（包含所有可用的 LoRA）
  - 当前使用的 LoRA
  - 镜像站信息

## 使用方法

### 前端操作

1. **选择 LoRA**:
   - 在页面上的 "LoRA 预设" 下拉菜单中选择
   - 选择后会显示 LoRA 的详细信息（路径、强度、描述）

2. **查看预设信息**:
   - 选择器下方会显示选中 LoRA 的描述
   - 显示 LoRA 路径和强度信息

### 后端配置

LoRA 选择器通过以下方式工作：
1. 前端从 `/api/lora-presets` 获取预设列表
2. 用户选择后，值存储在 `pipelineValues.lora_selection` 中
3. 注意：当前实现中，LoRA 在初始化时加载，运行时切换需要重启服务

## 文件修改清单

### 新增文件
- `frontend/src/lib/components/LoraSelector.svelte` - LoRA 选择器组件

### 修改文件
- `frontend/src/routes/+page.svelte` - 主页面（中文化）
- `frontend/src/lib/components/PipelineOptions.svelte` - 管道选项组件（集成 LoRA 选择器）
- `frontend/src/lib/components/TextArea.svelte` - 文本域组件（中文化占位符）
- `workflow.py` - 后端（页面内容中文化，添加 lora_selection 字段）

## 技术细节

### LoRA 选择器组件特性

1. **自动加载预设**: 组件挂载时自动从 API 获取预设列表
2. **错误处理**: 如果加载失败，显示错误信息
3. **加载状态**: 加载过程中显示 "加载中..."
4. **详细信息显示**: 显示选中 LoRA 的路径、强度和描述

### 数据流

```
用户选择 LoRA
  ↓
LoraSelector 组件更新 value
  ↓
绑定到 pipelineValues.lora_selection
  ↓
通过 WebSocket 发送到后端
  ↓
后端处理（需要重启服务以应用新的 LoRA）
```

## 后续改进建议

1. **运行时切换 LoRA**: 
   - 当前 LoRA 在初始化时加载，无法运行时切换
   - 可以实现动态重新加载 pipeline 的功能

2. **LoRA 预览**:
   - 添加 LoRA 效果预览图
   - 显示每个 LoRA 的示例图片

3. **自定义 LoRA 上传**:
   - 支持用户上传自己的 LoRA 文件
   - 支持输入 HuggingFace ID

4. **LoRA 强度调整**:
   - 在界面上直接调整 LoRA 强度
   - 实时预览效果

## 注意事项

1. **LoRA 切换**: 当前实现中，切换 LoRA 需要重启服务才能生效
2. **首次加载**: 首次访问时，LoRA 预设列表需要从 API 获取，可能需要一些时间
3. **网络要求**: 如果使用 HuggingFace LoRA，首次下载需要网络连接

