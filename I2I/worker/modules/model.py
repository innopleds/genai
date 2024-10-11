from diffusers import StableDiffusionXLImg2ImgPipeline, DPMSolverMultistepScheduler,AutoencoderKL
import torch

dpm = DPMSolverMultistepScheduler(
    beta_start=0.00085,
    beta_end=0.012,
    beta_schedule="scaled_linear"
)
def load_models():
    model_id = "stabilityai/stable-diffusion-xl-refiner-1.0"
    
    i2i_pipe = StableDiffusionXLImg2ImgPipeline.from_pretrained(
         model_id,
        # vae=vae,
        torch_dtype=torch.float16,
        use_safetensors=True,
        variant="fp16"
    ).to("cuda")
    
    i2i_pipe = i2i_pipe.to("cuda")
    return i2i_pipe
