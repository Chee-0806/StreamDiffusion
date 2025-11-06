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

# LoRA 预设列表（支持 HuggingFace ID 和本地路径）
# 使用 HuggingFace ID 格式：author/model-name
# 模型会自动从国内镜像站 (hf-mirror.com) 下载
# 注意：请确保模型 ID 在 HuggingFace Hub 上存在
LORA_PRESETS = [
    {
        "id": "none",
        "name": "无 LoRA",
        "path": None,
        "strength_model": 0.0,
        "description": "不使用任何 LoRA"
    },
    {
        "id": "anime_style",
        "name": "动漫风格",
        "path": "ostris/super-cereal-sdxl-lora",
        "strength_model": 0.8,
        "description": "动漫风格 LoRA (SDXL，适配 SD 1.5 需要确认)"
    },
    {
        "id": "realistic_vision",
        "name": "写实风格",
        "path": "sayakpaul/sd-model-finetuned-lora-t2i",
        "strength_model": 0.7,
        "description": "写实风格 LoRA"
    },
    {
        "id": "chinese_style",
        "name": "中国风",
        "path": "Linaqruf/anything-v3.0",
        "strength_model": 0.8,
        "description": "中国风风格 LoRA"
    },
    {
        "id": "watercolor",
        "name": "水彩风格",
        "path": "ostris/watercolor_style_lora",
        "strength_model": 0.75,
        "description": "水彩画风格 LoRA"
    },
    {
        "id": "oil_painting",
        "name": "油画风格",
        "path": "ostris/oil_painting_style_lora",
        "strength_model": 0.7,
        "description": "油画风格 LoRA"
    },
    # 示例：如何使用本地 LoRA 文件
    # {
    #     "id": "local_example",
    #     "name": "本地 LoRA 示例",
    #     "path": "models/LoRA/your_lora.safetensors",
    #     "strength_model": 0.8,
    #     "description": "本地 LoRA 文件示例"
    # },
]

# ComfyUI 工作流默认参数
default_prompt = "masterpiece,inflatable flowers,transparency,blue sky background,high quality,"
default_negative_prompt = "ng_deepnegative_v1_75t,(badhandv4:1.2),EasyNegative,(worst quality:2),balloon,,nsfw"

page_content = """<h1 class="text-3xl font-bold">StreamDiffusion</h1>
<h3 class="text-xl font-bold">ComfyUI 工作流 - 图像到图像</h3>
<p class="text-sm">
    本演示展示了使用 ComfyUI 工作流参数的 StreamDiffusion。
    <br/>
    模型: stabilityai/sd-turbo
    <br/>
    LoRA: 支持从 HuggingFace 自动下载
    <br/>
    采样器: LCM, 步数=4, CFG=1.8, 去噪强度=0.6
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
    # 类变量：LoRA 预设列表
    LORA_PRESETS = LORA_PRESETS
    
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
        lora_selection: str = Field(
            "none",
            title="LoRA 预设",
            field="select",
            id="lora_selection",
            description="选择要使用的 LoRA 预设（从 HuggingFace 下载）",
            values=["none"]  # 默认值，实际值从 API 获取
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
        # 支持 HuggingFace ID 或本地路径
        # 注意：为了支持动态切换，我们不在这里融合 LoRA
        # 而是在初始化后单独加载，不调用 fuse_lora()
        lora_dict: Optional[Dict[str, float]] = None
        if args.lora_path:
            lora_path_str = args.lora_path
            
            # 判断是 HuggingFace ID 还是本地路径
            # HuggingFace ID 格式：author/model-name 或包含 / 但不以 .safetensors 结尾且不是绝对路径
            is_hf_id = (
                "/" in lora_path_str 
                and not lora_path_str.endswith((".safetensors", ".ckpt", ".pt", ".pth"))
                and not Path(lora_path_str).is_absolute()
                and not Path(lora_path_str).exists()
            )
            
            if is_hf_id:
                # HuggingFace ID，直接使用（会从镜像站下载）
                lora_dict = {lora_path_str: args.lora_strength_model}
                print(f"使用 HuggingFace LoRA: {lora_path_str} (强度: {args.lora_strength_model})")
            else:
                # 本地路径，尝试查找文件
                lora_full_path = Path(lora_path_str)
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
                        print(f"找到本地 LoRA 文件: {lora_full_path} (强度: {args.lora_strength_model})")
                else:
                    lora_dict = {str(lora_full_path): args.lora_strength_model}
                    print(f"使用本地 LoRA 文件: {lora_full_path} (强度: {args.lora_strength_model})")
        
        # 为了支持动态切换，我们不通过 wrapper 加载 LoRA
        # 而是在初始化后单独加载，不融合
        # 保存初始 LoRA 信息，稍后加载
        initial_lora_path = None
        initial_lora_strength = args.lora_strength_model
        if lora_dict:
            initial_lora_path = list(lora_dict.keys())[0]
            initial_lora_strength = list(lora_dict.values())[0]
            # 不传递给 wrapper，避免融合
            lora_dict = None
        
        self.stream = StreamDiffusionWrapper(
            model_id_or_path=model_path_str,
            lora_dict=None,  # 不在这里加载 LoRA，支持动态切换
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
        self.args = args  # 保存 args 以便后续使用
        self.base_model_path = model_path_str  # 保存基础模型路径
        self.is_turbo = is_turbo  # 保存是否为 Turbo 模型
        self.t_index_list = t_index_list  # 保存 t_index_list
        self._lora_fused = False  # 标记 LoRA 是否已融合
        
        # 准备模型
        self.stream.prepare(
            prompt=default_prompt,
            negative_prompt=default_negative_prompt,
            num_inference_steps=50,
            guidance_scale=params.cfg_scale,
        )
        
        # 如果初始有 LoRA，加载但不融合（以支持动态切换）
        if initial_lora_path:
            try:
                # 直接加载，不融合
                self.stream.stream.pipe.load_lora_weights(initial_lora_path)
                print(f"初始加载 LoRA: {initial_lora_path} (未融合，强度: {initial_lora_strength})")
                print("提示: 未融合的 LoRA 支持动态切换，但可能影响性能")
                self.current_lora = initial_lora_path
                self.current_lora_strength = initial_lora_strength
            except Exception as e:
                print(f"初始加载 LoRA 失败: {e}")
                print("提示: 将尝试使用融合模式（不支持动态切换）")
                # 如果失败，回退到融合方式（但无法动态切换）
                try:
                    self.stream.stream.load_lora(initial_lora_path)
                    self.stream.stream.fuse_lora(lora_scale=initial_lora_strength)
                    print(f"回退到融合模式加载 LoRA: {initial_lora_path}")
                    self.current_lora = initial_lora_path
                    self.current_lora_strength = initial_lora_strength
                    self._lora_fused = True  # 标记为已融合，无法动态切换
                except Exception as e2:
                    print(f"融合模式加载也失败: {e2}")
                    self.current_lora = None
                    self.current_lora_strength = 0.0
        else:
            self.current_lora = None
            self.current_lora_strength = 0.0

    def switch_lora(self, lora_selection: str) -> bool:
        """
        动态切换 LoRA（不重启服务）
        
        Parameters
        ----------
        lora_selection : str
            LoRA 预设 ID，从 LORA_PRESETS 中获取
        
        Returns
        -------
        bool
            是否切换成功
        """
        # 检查是否支持动态切换（LoRA 未被融合）
        if getattr(self, '_lora_fused', False):
            print("警告: 当前 LoRA 已融合，无法动态切换。需要重启服务。")
            return False
            
        try:
            # 查找对应的预设
            preset = None
            for p in LORA_PRESETS:
                if p["id"] == lora_selection:
                    preset = p
                    break
            
            if not preset:
                print(f"警告: 未找到 LoRA 预设 {lora_selection}")
                return False
            
            # 如果选择 "none"，卸载当前 LoRA
            if preset["path"] is None:
                if self.current_lora:
                    print(f"卸载当前 LoRA: {self.current_lora}")
                    self._unload_lora()
                    self.current_lora = None
                    self.current_lora_strength = 0.0
                return True
            
            # 获取 LoRA 路径
            lora_path = preset["path"]
            lora_strength = preset.get("strength_model", 0.8)
            
            # 判断是 HuggingFace ID 还是本地路径
            is_hf_id = (
                "/" in lora_path 
                and not lora_path.endswith((".safetensors", ".ckpt", ".pt", ".pth"))
                and not Path(lora_path).is_absolute()
                and not Path(lora_path).exists()
            )
            
            if not is_hf_id:
                # 本地路径，尝试查找文件
                lora_full_path = Path(lora_path)
                if not lora_full_path.exists():
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
                        print(f"警告: 未找到 LoRA 文件 {lora_path}")
                        return False
                    lora_path = str(lora_full_path)
            
            # 如果和当前 LoRA 相同，不需要切换
            if self.current_lora == lora_path and self.current_lora_strength == lora_strength:
                print(f"LoRA 已加载: {lora_path}")
                return True
            
            # 卸载当前 LoRA（如果存在）
            if self.current_lora:
                print(f"卸载当前 LoRA: {self.current_lora}")
                self._unload_lora()
            
            # 加载新的 LoRA
            print(f"加载 LoRA: {lora_path} (强度: {lora_strength})")
            self._load_lora(lora_path, lora_strength)
            
            self.current_lora = lora_path
            self.current_lora_strength = lora_strength
            
            return True
            
        except Exception as e:
            print(f"切换 LoRA 失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _load_lora(self, lora_path: str, lora_scale: float):
        """加载 LoRA（动态加载，不融合以支持切换）"""
        try:
            # 直接使用 pipe 的 load_lora_weights，不融合
            # 这样可以使用 unload_lora_weights 来卸载
            self.stream.stream.pipe.load_lora_weights(lora_path)
            # 注意：不调用 fuse_lora()，以支持动态切换
            # 但这样可能会影响性能，因为每次推理都需要应用 LoRA
            # 如果性能问题严重，可以考虑使用 adapter 系统
            print(f"已加载 LoRA: {lora_path} (未融合，强度: {lora_scale})")
            print("提示: 未融合的 LoRA 可能影响性能，但支持动态切换")
        except Exception as e:
            print(f"加载 LoRA 失败: {e}")
            raise
    
    def _unload_lora(self):
        """卸载当前 LoRA"""
        try:
            # 使用 diffusers 的 unload_lora_weights 方法
            if hasattr(self.stream.stream.pipe, 'unload_lora_weights'):
                self.stream.stream.pipe.unload_lora_weights()
                print("已卸载 LoRA")
            elif hasattr(self.stream.stream.pipe, 'disable_lora'):
                # 备用方案：禁用 LoRA
                self.stream.stream.pipe.disable_lora()
                print("已禁用 LoRA")
            else:
                print("警告: 当前 diffusers 版本不支持动态卸载 LoRA")
                print("提示: 可能需要重新加载模型才能切换 LoRA")
        except Exception as e:
            print(f"卸载 LoRA 时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def predict(self, params: "Pipeline.InputParams") -> Image.Image:
        # 检查 LoRA 是否需要切换
        if hasattr(params, 'lora_selection') and params.lora_selection:
            if params.lora_selection != getattr(self, '_last_lora_selection', 'none'):
                print(f"检测到 LoRA 切换请求: {params.lora_selection}")
                success = self.switch_lora(params.lora_selection)
                if success:
                    self._last_lora_selection = params.lora_selection
                else:
                    print(f"LoRA 切换失败，继续使用当前 LoRA")
        
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

