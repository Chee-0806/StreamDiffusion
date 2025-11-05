import sys
import os
from pathlib import Path
from typing import Dict, Optional

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
    )
)

from utils.wrapper import StreamDiffusionWrapper

import torch

from config import Args
from pydantic import BaseModel, Field
from PIL import Image

# 默认模型（使用 sd-turbo，与 realtime-img2img 一致）
base_model = "stabilityai/sd-turbo"

# ComfyUI 工作流默认参数
default_prompt = "masterpiece,inflatable flowers,transparency,blue sky background,high quality,"
default_negative_prompt = "ng_deepnegative_v1_75t,(badhandv4:1.2),EasyNegative,(worst quality:2),balloon,,nsfw"

page_content = """<h1 class="text-3xl font-bold">StreamDiffusion</h1>
<h3 class="text-xl font-bold">ComfyUI Workflow - Image-to-Image</h3>
<p class="text-sm">
    This demo showcases StreamDiffusion with ComfyUI workflow parameters.
    <br/>
    Model: realisticVisionV60B1_v51HyperVAE
    <br/>
    LoRA: 充气花朵_v1.0
    <br/>
    KSampler: LCM, steps=4, cfg=1.8, denoise=0.6
</p>
"""


def calculate_t_index_list(steps: int, denoise: float, num_inference_steps: int = 50) -> list:
    """
    根据 denoise 强度和步数计算 t_index_list
    
    Parameters
    ----------
    steps : int
        采样步数
    denoise : float
        去噪强度 (0.0-1.0)，1.0 表示完全重新生成，0.0 表示几乎不改变
    num_inference_steps : int
        总推理步数，默认 50
    
    Returns
    -------
    list
        t_index_list，从高噪声到低噪声排序
    """
    start_index = int(num_inference_steps * denoise)
    start_index = min(num_inference_steps - 1, max(0, start_index))
    
    if steps == 1:
        return [start_index]
    
    indices = []
    if steps > 1:
        step_size = start_index / (steps - 1)
    else:
        step_size = 0
    
    for i in range(steps):
        idx = int(start_index - i * step_size)
        indices.append(max(0, idx))
    
    indices = sorted(set(indices), reverse=True)
    
    if start_index not in indices:
        indices.append(start_index)
    if 0 not in indices:
        indices.append(0)
    
    indices = sorted(set(indices), reverse=True)
    
    if len(indices) > steps:
        selected = [indices[0]]
        if steps > 2:
            step = (indices[0] - indices[-1]) / (steps - 1)
            for i in range(1, steps - 1):
                idx = int(indices[0] - i * step)
                selected.append(idx)
        selected.append(indices[-1])
        indices = sorted(set(selected), reverse=True)
    
    return indices


class Pipeline:
    class Info(BaseModel):
        name: str = "StreamDiffusion ComfyUI Workflow"
        input_mode: str = "image"
        page_content: str = page_content

    class InputParams(BaseModel):
        prompt: str = Field(
            default_prompt,
            title="Prompt",
            field="textarea",
            id="prompt",
        )
        negative_prompt: str = Field(
            default_negative_prompt,
            title="Negative Prompt",
            field="textarea",
            id="negative_prompt",
        )
        width: int = Field(
            512, min=2, max=15, title="Width", disabled=True, hide=True, id="width"
        )
        height: int = Field(
            512, min=2, max=15, title="Height", disabled=True, hide=True, id="height"
        )
        # ComfyUI KSampler 参数
        steps: int = Field(
            4, min=1, max=10, title="Steps", id="steps"
        )
        cfg_scale: float = Field(
            1.8, min=1.0, max=20.0, title="CFG Scale", id="cfg_scale"
        )
        denoise: float = Field(
            0.6, min=0.0, max=1.0, title="Denoise Strength", id="denoise"
        )
        seed: int = Field(
            502923423887318, title="Seed", id="seed"
        )

    def __init__(self, args: Args, device: torch.device, torch_dtype: torch.dtype):
        params = self.InputParams()
        
        # 检查模型路径
        # 如果提供的是本地文件路径且不存在，尝试使用默认模型
        model_path_str = args.model_path
        model_path = Path(args.model_path)
        
        # 检查是否是本地文件路径
        if not model_path.exists() and not model_path.is_absolute():
            # 尝试在常见路径中查找
            common_paths = [
                Path("models") / "Stable-diffusion" / model_path.name,
                Path("models/Stable-diffusion") / model_path.name,
                Path("..") / ".." / "models" / "Stable-diffusion" / model_path.name,
                model_path,
            ]
            found = False
            for path in common_paths:
                if path.exists():
                    model_path_str = str(path)
                    found = True
                    print(f"找到模型文件: {model_path_str}")
                    break
            
            # 如果本地文件不存在，且不是 HuggingFace ID 格式，使用默认模型
            if not found and "/" not in args.model_path and "\\" not in args.model_path:
                print(f"警告: 未找到本地模型文件 {args.model_path}")
                print(f"将使用默认模型: {base_model}")
                model_path_str = base_model
        elif not model_path.exists() and ("/" in args.model_path or args.model_path.startswith("http")):
            # 看起来是 HuggingFace ID 或 URL，直接使用
            model_path_str = args.model_path
            print(f"使用 HuggingFace 模型: {model_path_str}")
        else:
            model_path_str = str(args.model_path)
            print(f"使用模型路径: {model_path_str}")
        
        # 判断是否是 SD-Turbo 模型
        is_turbo = "turbo" in model_path_str.lower()
        
        # 计算 t_index_list（SD-Turbo 优化配置）
        if is_turbo:
            # SD-Turbo 性能优化：单步 [45] 最快（~94 fps），2步 [35, 45] 质量稍好但较慢
            # 可通过环境变量 TURBO_STEPS 控制：1=单步（最快），2=双步（默认，质量更好）
            turbo_steps = int(os.environ.get("TURBO_STEPS", "2"))
            if turbo_steps == 1:
                t_index_list = [45]  # 单步模式，最快速度
                print(f"使用 SD-Turbo（单步模式，最快速度），t_index_list: {t_index_list}")
            else:
                t_index_list = [35, 45]  # 双步模式，质量更好
                print(f"使用 SD-Turbo（双步模式，平衡质量和速度），t_index_list: {t_index_list}")
        else:
            t_index_list = calculate_t_index_list(params.steps, params.denoise)
            print(f"计算的 t_index_list: {t_index_list}")
        
        # 准备 LoRA 字典
        lora_dict: Optional[Dict[str, float]] = None
        if args.lora_path:
            lora_full_path = Path(args.lora_path)
            if not lora_full_path.exists():
                # 尝试在常见路径中查找
                common_paths = [
                    Path("models/Lora") / lora_full_path.name,
                    Path("models/lora") / lora_full_path.name,
                    Path("lora") / lora_full_path.name,
                    Path("..") / ".." / "models" / "lora" / lora_full_path.name,
                    lora_full_path,
                ]
                found = False
                for path in common_paths:
                    if path.exists():
                        lora_full_path = path
                        found = True
                        break
                if not found:
                    print(f"警告: 未找到 LoRA 文件 {args.lora_path}，将跳过 LoRA 加载")
                else:
                    lora_dict = {str(lora_full_path): args.lora_strength_model}
                    print(f"找到 LoRA 文件: {lora_full_path}")
            else:
                lora_dict = {str(lora_full_path): args.lora_strength_model}
        
        self.stream = StreamDiffusionWrapper(
            model_id_or_path=model_path_str,
            lora_dict=lora_dict,
            t_index_list=t_index_list,
            frame_buffer_size=1,
            width=params.width,
            height=params.height,
            warmup=10,
            acceleration=args.acceleration,
            mode="img2img",
            use_denoising_batch=True,
            cfg_type="none" if is_turbo else ("self" if params.cfg_scale > 1.0 else "none"),  # SD-Turbo 使用 cfg_type="none"
            seed=params.seed,
            use_lcm_lora=False if is_turbo else True,  # SD-Turbo 不需要 LCM LoRA
            use_tiny_vae=args.taesd,  # 如果 checkpoint 已包含 VAE，可以设置为 False
            output_type="pil",
            use_safety_checker=args.safety_checker,
            engine_dir=args.engine_dir,
        )

        self.last_prompt = default_prompt
        self.last_negative_prompt = default_negative_prompt
        self.last_cfg_scale = params.cfg_scale
        self.last_steps = params.steps
        self.last_denoise = params.denoise
        self.last_seed = params.seed
        
        # 准备模型
        self.stream.prepare(
            prompt=default_prompt,
            negative_prompt=default_negative_prompt,
            num_inference_steps=50,
            guidance_scale=params.cfg_scale,
        )

    def predict(self, params: "Pipeline.InputParams") -> Image.Image:
        # 检查参数是否变化，如果变化则重新准备
        need_reprepare = (
            params.prompt != self.last_prompt
            or params.negative_prompt != self.last_negative_prompt
            or params.cfg_scale != self.last_cfg_scale
        )
        
        if need_reprepare:
            # 注意：StreamDiffusion 不支持动态修改 t_index_list
            # 如果需要修改 steps 或 denoise，需要重新创建 StreamDiffusionWrapper
            # 这里只更新提示词和 CFG scale
            if params.cfg_scale != self.last_cfg_scale or params.negative_prompt != self.last_negative_prompt:
                # 重新准备以更新 CFG scale 和 negative prompt
                self.stream.prepare(
                    prompt=params.prompt,
                    negative_prompt=params.negative_prompt,
                    num_inference_steps=50,
                    guidance_scale=params.cfg_scale,
                )
            else:
                # 只更新 prompt
                self.stream.update_prompt(params.prompt)
            
            self.last_prompt = params.prompt
            self.last_negative_prompt = params.negative_prompt
            self.last_cfg_scale = params.cfg_scale
        
        image_tensor = self.stream.preprocess_image(params.image)
        output_image = self.stream(image=image_tensor, prompt=params.prompt)

        return output_image

