# 性能优化指南

## 当前配置分析

根据官方基准测试（RTX 4090），SD-Turbo 的性能表现：

| 模型 | 去噪步数 | Img2Img FPS |
|------|---------|-------------|
| SD-Turbo | 1步 | **93.897** |
| SD-Turbo | 2步 | ~50-60 (估算) |
| LCM-LoRA + KohakuV2 | 4步 | 37.133 |

## 性能优化选项

### 1. 使用单步模式（最快速度）

**设置环境变量**：
```bash
export TURBO_STEPS=1
bash start.sh
```

**效果**：
- ✅ 速度最快（理论值 ~94 fps）
- ⚠️ 质量可能略低于双步模式

### 2. 使用双步模式（平衡质量和速度，默认）

**设置环境变量**：
```bash
export TURBO_STEPS=2
bash start.sh
```

或者直接运行（默认就是双步）：
```bash
bash start.sh
```

**效果**：
- ✅ 质量更好
- ⚠️ 速度较慢（约 50-60 fps）

### 3. 其他优化建议

#### ✅ 已优化的配置：
- ✓ 使用 SD-Turbo（最快的模型）
- ✓ TensorRT 加速已启用
- ✓ Tiny VAE (TAESD) 已启用
- ✓ 分辨率 512x512（最小推荐值）
- ✓ frame_buffer_size=1（img2img 模式）
- ✓ cfg_type="none"（SD-Turbo 不需要 CFG）

#### 🔧 可以尝试的优化：

1. **降低分辨率**（如果可接受）：
   - 当前：512x512
   - 可以尝试：384x384（会更快，但质量下降）

2. **检查 TensorRT 引擎是否已构建**：
   ```bash
   ls -lh engines/stabilityai/sd-turbo-*/
   ```
   - 首次运行需要构建引擎（慢）
   - 后续运行直接使用缓存的引擎（快）

3. **检查 GPU 利用率**：
   ```bash
   nvidia-smi -l 1
   ```
   - 如果 GPU 利用率 < 90%，可能还有其他瓶颈

4. **网络延迟**：
   - 如果通过远程访问，网络传输也会影响实时性
   - 建议在本地测试以获得最佳体验

## 性能对比

### 单步模式 (TURBO_STEPS=1)
- **t_index_list**: [45]
- **预期 FPS**: ~90-95 fps
- **适用场景**: 追求极致速度，实时交互

### 双步模式 (TURBO_STEPS=2，默认)
- **t_index_list**: [35, 45]
- **预期 FPS**: ~50-60 fps
- **适用场景**: 平衡质量和速度

## 诊断工具

### 检查当前配置
```bash
cd /root/StreamDiffusion/demo/realtime-comfyui-workflow
source /root/autodl-tmp/venv/bin/activate
python << 'EOF'
import os
print("当前配置：")
print(f"  TURBO_STEPS: {os.environ.get('TURBO_STEPS', '2 (默认)')}")
print(f"  模型: stabilityai/sd-turbo")
print(f"  加速: tensorrt")
print(f"  Tiny VAE: True")
EOF
```

### 性能测试
运行程序后，观察控制台输出的 FPS 信息（如果有），或者通过前端界面感受响应速度。

## 如果仍然不够快

1. **检查 TensorRT 是否真正启用**：
   - 查看日志中是否有 "TensorRT acceleration enabled"
   - 如果没有，检查 TensorRT 引擎是否已构建

2. **检查是否有其他进程占用 GPU**：
   ```bash
   nvidia-smi
   ```

3. **尝试关闭不必要的功能**：
   - 确保没有启用 safety_checker
   - 确保使用 Tiny VAE

4. **考虑硬件因素**：
   - RTX 4090 应该能达到很好的性能
   - 如果使用其他 GPU，性能会相应降低

