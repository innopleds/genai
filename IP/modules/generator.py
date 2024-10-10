from PIL import Image
from dotenv import load_dotenv
from fastapi.responses import FileResponse
import torch
import os
from datetime import datetime
from modules.model import load_models
from modules.schemas import IPRequest, IPResponse 
import modules.externel_api as api
import modules.dataloader as _dl


load_dotenv()
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
api.mem_usage()
ip_pipe = load_models()
api.mem_usage()
counter = 1

async def generate_ip_image(request: IPRequest, input_img_path: str, mask_img_path: str, output_dir: str) -> IPResponse:
    global counter  
    prompts = await _dl.load_json('./fixed_prompt.json')
    input_prompt = prompts['fixed_prompt'] + await api.deepl_translate(request.prompt)
    input_negative = prompts['fixed_neg_prompt'] + await api.deepl_translate(request.negative)

    image_urls = []
    bucket_name = AWS_BUCKET_NAME
    
    input_img = Image.open(input_img_path).convert("RGB")
    mask_img = Image.open(mask_img_path).convert("L")
    
    today = datetime.today().strftime('%Y%m%d')
    now = datetime.now().strftime('%H%M%S')
    counter_str = f"{counter:04d}"  
    subfolder = f"genai/ip/{today}/{today}-{now}-{counter_str}"
    
    print("Before running function 'a':")
    await api.print_gpu_memory()
    memory_before = await api.get_gpu_memory()
    if request.model_choice == "Realistic":
        imgs = ip_pipe(
            prompt=input_prompt,
            negative_prompt=input_negative,
            image=input_img,
            mask_image=mask_img,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.cfg_scale,
            width=request.width,
            height=request.height,
            strength=request.denoising_strength,
            generator = torch.Generator(device="cuda").manual_seed(request.seed),
            # seed=request.seed,
            # padding_mask_crop=16, # same effect as “Only masked” area inpainting
            num_images_per_prompt=request.batch_count
        ).images
        print(f"prompt={input_prompt},")
        print(f"negative_prompt={input_negative},")
        print(f"seed={request.seed}")
        for img in imgs:
            img_path = await _dl.save_image(img, output_dir)
            image_url = await _dl.upload_to_temp_s3(img_path, bucket_name, subfolder)
            image_urls.append(image_url)
            
        # del imgs
        # torch.cuda.empty_cache()
        counter += 1
        print("\nAfter running function 'a':")
        await api.print_gpu_memory()
        memory_after = await api.get_gpu_memory()
        
        # api.mem_usage()
        memory_diff = memory_after - memory_before
        print(f"\nMemory usage difference: {memory_diff}MB")
    else:
        raise ValueError("Unsupported model choice")
   
    return IPResponse(prompt=input_prompt, image_urls=image_urls, seed=request.seed)



# def input_prompts(gpt_api, prompts, prompt: str) -> str:
#     if gpt_api==False:
#         input_prompt = prompts['fixed_prompt'] + api.deepl_translate(prompt)
#     else:
#         print('gpt_api')
#         # input_prompt = prompts['fixed_prompt'] + api.gen_keyword(prompt)
            
#     return input_prompt