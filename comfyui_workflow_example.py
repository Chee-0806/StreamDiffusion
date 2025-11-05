"""
将 ComfyUI 工作流转换为 StreamDiffusion 的示例脚本

工作流参数：
- Checkpoint: realisticVisionV60B1_v51HyperVAE.safetensors
- LoRA: 1.5\充气花朵_v1.0.safetensors (strength_model: 0.8, strength_clip: 1.0)
- 输入图像: 86d4a0913d90aa71c0377f0b980c6274.jpg
- KSampler: steps=4, cfg=1.8, sampler=lcm, scheduler=normal, denoise=0.6, seed=502923423887318
- 正面提示词: masterpiece,inflatable flowers,transparency,blue sky background,high quality,
- 负面提示词: ng_deepnegative_v1_75t,(badhandv4:1.2),EasyNegative,(worst quality:2),balloon,,nsfw
"""

import os
import sys
from typing import Dict, Optional
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.dirname(__file__))

from utils.wrapper import StreamDiffusionWrapper

# ==================== 配置参数 ====================
# 模型路径（请根据实际情况修改）
MODEL_PATH = "realisticVisionV60B1_v51HyperVAE.safetensors"  # 可以是本地路径或 HuggingFace ID

# LoRA 配置
# 注意：StreamDiffusion 的 lora_dict 中，值对应 strength_model
# strength_clip 在 StreamDiffusion 中通过 fuse_lora 的 fuse_text_encoder 参数控制
LORA_PATH = r"1.5\充气花朵_v1.0.safetensors"  # 请根据实际路径修改
LORA_STRENGTH_MODEL = 0.8  # 对应 ComfyUI 的 strength_model
LORA_STRENGTH_CLIP = 1.0   # 对应 ComfyUI 的 strength_clip（在 StreamDiffusion 中通过 fuse_text_encoder 控制）

# 输入图像路径
INPUT_IMAGE = "86d4a0913d90aa71c0377f0b980c6274.jpg"  # 请根据实际路径修改

# 输出图像路径
OUTPUT_IMAGE = "output.png"

# KSampler 参数
STEPS = 4
CFG_SCALE = 1.8
DENOISE_STRENGTH = 0.6  # 0.6 表示从 60% 的噪声开始
SEED = 502923423887318

# 提示词
PROMPT = "masterpiece,inflatable flowers,transparency,blue sky background,high quality,"
NEGATIVE_PROMPT = "ng_deepnegative_v1_75t,(badhandv4:1.2),EasyNegative,(worst quality:2),balloon,,nsfw"

# 图像尺寸（根据输入图像自动调整，或手动设置）
WIDTH = 512
HEIGHT = 512

# 加速方式
ACCELERATION = "xformers"  # 可选: "none", "xformers", "tensorrt"

# ==================== 计算 t_index_list ====================
# 对于 denoise=0.6 和 steps=4，我们需要选择合适的 t_index_list
# denoise=0.6 意味着从 60% 的噪声开始（保留 40% 的原始图像信息）
# 在 LCM 调度器中，通常使用 50 步，denoise=0.6 对应大约从索引 30 开始
# 对于 4 步，我们选择均匀分布的索引
def calculate_t_index_list(steps: int, denoise: float, num_inference_steps: int = 50) -> list:
    """
    根据 denoise 强度和步数计算 t_index_list
    
    Parameters
    ----------
    steps : int
        采样步数
    denoise : float
        去噪强度 (0.0-1.0)，1.0 表示完全重新生成，0.0 表示几乎不改变
        ComfyUI 中 denoise=0.6 表示从 60% 的噪声开始
    num_inference_steps : int
        总推理步数，默认 50
    
    Returns
    -------
    list
        t_index_list，从高噪声到低噪声排序
    """
    # denoise=0.6 意味着从 60% 的噪声开始
    # 在 LCM 调度器中，timesteps 是从高到低排列的
    # 对于 50 步，索引 0 对应最高噪声，索引 49 对应最低噪声
    # denoise=0.6 意味着从 60% 的噪声开始，即从索引 30 左右开始 (50 * 0.6 = 30)
    start_index = int(num_inference_steps * denoise)
    
    # 确保索引在有效范围内
    start_index = min(num_inference_steps - 1, max(0, start_index))
    
    if steps == 1:
        return [start_index]
    
    # 从 start_index 开始，均匀分布到接近最高噪声（索引 0）
    # 例如：denoise=0.6, steps=4, start_index=30
    # 可以设置为 [30, 20, 10, 0] 或更均匀的分布
    indices = []
    
    # 计算步长
    if steps > 1:
        step_size = start_index / (steps - 1)
    else:
        step_size = 0
    
    # 生成索引，从 start_index 到 0
    for i in range(steps):
        idx = int(start_index - i * step_size)
        indices.append(max(0, idx))
    
    # 去重并排序（从大到小，因为 LCM 调度器从高噪声到低噪声）
    indices = sorted(set(indices), reverse=True)
    
    # 确保至少包含 start_index 和 0
    if start_index not in indices:
        indices.append(start_index)
    if 0 not in indices:
        indices.append(0)
    
    # 重新排序
    indices = sorted(set(indices), reverse=True)
    
    # 如果索引数量超过 steps，选择均匀分布的索引
    if len(indices) > steps:
        selected = [indices[0]]  # 总是包含第一个（最高噪声）
        if steps > 2:
            step = (indices[0] - indices[-1]) / (steps - 1)
            for i in range(1, steps - 1):
                idx = int(indices[0] - i * step)
                selected.append(idx)
        selected.append(indices[-1])  # 总是包含最后一个（最低噪声）
        indices = sorted(set(selected), reverse=True)
    
    return indices

# 计算 t_index_list
T_INDEX_LIST = calculate_t_index_list(STEPS, DENOISE_STRENGTH)
print(f"计算的 t_index_list: {T_INDEX_LIST}")

# ==================== 主函数 ====================
def main():
    """执行 ComfyUI 工作流"""
    
    # 准备 LoRA 字典
    lora_dict: Optional[Dict[str, float]] = None
    if LORA_PATH:
        # 检查 LoRA 文件是否存在
        lora_full_path = Path(LORA_PATH)
        if not lora_full_path.exists():
            # 尝试在常见路径中查找
            common_paths = [
                Path("models/Lora") / lora_full_path.name,
                Path("models/lora") / lora_full_path.name,
                Path("lora") / lora_full_path.name,
                lora_full_path,
            ]
            found = False
            for path in common_paths:
                if path.exists():
                    lora_full_path = path
                    found = True
                    break
            if not found:
                print(f"警告: 未找到 LoRA 文件 {LORA_PATH}，将跳过 LoRA 加载")
                lora_dict = None
            else:
                lora_dict = {str(lora_full_path): LORA_STRENGTH_MODEL}
                print(f"找到 LoRA 文件: {lora_full_path}")
        else:
            lora_dict = {str(lora_full_path): LORA_STRENGTH_MODEL}
    
    # 检查模型文件
    model_path = Path(MODEL_PATH)
    if not model_path.exists():
        # 尝试作为 HuggingFace ID 或本地路径
        print(f"尝试加载模型: {MODEL_PATH}")
        # 如果不存在，StreamDiffusion 会尝试从 HuggingFace 加载
    
    # 检查输入图像
    input_image_path = Path(INPUT_IMAGE)
    if not input_image_path.exists():
        print(f"错误: 未找到输入图像 {INPUT_IMAGE}")
        return
    
    # 创建 StreamDiffusion 包装器
    print("正在初始化 StreamDiffusion...")
    
    # 注意：如果 LoRA 的 strength_clip 和 strength_model 不同，
    # 我们需要在加载后手动调整
    # 这里先使用 strength_model 作为默认值
    stream = StreamDiffusionWrapper(
        model_id_or_path=str(MODEL_PATH),
        lora_dict=lora_dict,
        t_index_list=T_INDEX_LIST,
        frame_buffer_size=1,
        width=WIDTH,
        height=HEIGHT,
        warmup=10,
        acceleration=ACCELERATION,
        mode="img2img",
        use_denoising_batch=True,
        cfg_type="self" if CFG_SCALE > 1.0 else "none",  # CFG > 1.0 时使用 RCFG
        seed=SEED,
        use_lcm_lora=True,  # 使用 LCM LoRA（对应 sampler=lcm）
        use_tiny_vae=False,  # 如果 checkpoint 已包含 VAE，可以设置为 False
    )
    
    # 如果 LoRA 的 strength_clip 和 strength_model 不同，需要手动调整
    # 注意：StreamDiffusion 的 fuse_lora 默认会同时融合 UNet 和 Text Encoder
    # 如果需要分别设置，需要在 _load_model 之后手动操作
    # 但由于 wrapper 的限制，这里暂时使用 strength_model 作为统一值
    # 如果需要精确控制，可以考虑修改 wrapper 或直接使用 StreamDiffusion 类
    
    # 准备模型
    print("正在准备模型...")
    stream.prepare(
        prompt=PROMPT,
        negative_prompt=NEGATIVE_PROMPT,
        num_inference_steps=50,  # LCM 调度器通常使用 50 步
        guidance_scale=CFG_SCALE,
        delta=1.0,  # RCFG 的 delta 参数
    )
    
    # 预处理输入图像
    print(f"正在加载输入图像: {INPUT_IMAGE}")
    image_tensor = stream.preprocess_image(str(input_image_path))
    
    # 预热（warmup）
    print("正在预热模型...")
    for i in range(stream.batch_size - 1):
        stream(image=image_tensor)
        print(f"预热步骤 {i+1}/{stream.batch_size-1}")
    
    # 执行推理
    print("正在生成图像...")
    output_image = stream(image=image_tensor)
    
    # 保存输出图像
    output_path = Path(OUTPUT_IMAGE)
    output_image.save(output_path)
    print(f"图像已保存到: {output_path}")
    
    print("完成！")


if __name__ == "__main__":
    main()

