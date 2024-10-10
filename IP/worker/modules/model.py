from diffusers import StableDiffusionInpaintPipeline, DPMSolverMultistepScheduler,AutoencoderKL
import torch

dpm = DPMSolverMultistepScheduler(
    beta_start=0.00085,
    beta_end=0.012,
    beta_schedule="scaled_linear"
)

# stabilityai/stable-diffusion-2-inpainting
# runwayml/stable-diffusion-inpainting
# Lykon/DreamShaper
# holwech/realistic-vision-5_1-optimized
# diffusers/stable-diffusion-xl-1.0-inpainting-0.1
# friedrichor/stable-diffusion-2-1-realistic

def load_models():
    model_id = "holwech/realistic-vision-5_1-optimized"
    
    ip_pipe = StableDiffusionInpaintPipeline.from_pretrained(
        model_id,
        # vae=vae,
        torch_dtype=torch.float16,
        use_safetensors=True,
        variant="fp16"
    ).to("cuda")
    
    ip_pipe.scheduler = dpm

    return ip_pipe

# repo_id = "./model/majicmixRealistic_v7.safetensors"
# repo_id = "./model/beautifulRealistic_v7.safetensors"
# repo_id = "./model/l8IpUITmG55STCzq_yLsf.safetensors"
# repo_id = "./model/rpgInpainting_v4-inpainting.safetensors"

# def load_models():
#     repo_id = "./model/beautifulRealistic_v7.safetensors"
#     ip_pipe = StableDiffusionInpaintPipeline.from_single_file(
#         repo_id,
#         torch_dtype=torch.float16,
#         use_safetensors=True,
#         variant="fp16"
#     ).to("cuda")
    
#     ip_pipe.scheduler = dpm

#     return ip_pipe