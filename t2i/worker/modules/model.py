from diffusers import StableDiffusionXLPipeline, DPMSolverMultistepScheduler,AutoencoderKL,DiffusionPipeline,StableDiffusionXLImg2ImgPipeline
import torch

dpm = DPMSolverMultistepScheduler(
    beta_start=0.00085,
    beta_end=0.012,
    beta_schedule="scaled_linear"
)

# def load_models():
#     t2i_pipe = StableDiffusionXLPipeline.from_pretrained(
#         "stabilityai/stable-diffusion-xl-base-1.0", torch_dtype=torch.float16, use_safetensors=True, 
#         variant="fp16"
#     )
#     t2i_pipe = t2i_pipe.to("cuda")
#     t2i_pipe.scheduler = dpm
#     return t2i_pipe

dpm2 = DPMSolverMultistepScheduler(
    beta_start=0.00085,
    beta_end=0.012,
    beta_schedule="scaled_linear"
)

def load_models():
    model_id = "stabilityai/stable-diffusion-xl-base-1.0"
    vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)
    t2i_pipe = StableDiffusionXLPipeline.from_pretrained(
        model_id, 
        vae=vae, 
        torch_dtype=torch.float16,
        use_safetensors=True,
        variant="fp16"
    ).to("cuda")
    
    refiner = StableDiffusionXLImg2ImgPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-refiner-1.0",
        vae=vae,
        torch_dtype=torch.float16, 
        use_safetensors=True, 
        variant="fp16"
    ).to("cuda")
    

    return t2i_pipe, refiner 