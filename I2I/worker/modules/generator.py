from PIL import Image
from dotenv import load_dotenv
import torch
import os
from datetime import datetime

from modules.model import load_models
from modules.schemas import I2IRequest, I2IResponse 
import modules.externel_api as api
import modules.dataloader as _dl
import modules.exe_query as _eq

load_dotenv()

AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

i2i_pipe = load_models()

counter = 1

async def generate_i2i_image(request: I2IRequest, result_image_id, input_img: Image.Image, output_dir: str) -> I2IResponse:
    global counter     
    prompts = await _dl.load_json('./fixed_prompt.json')   
    user_prompt_en = await api.deepl_translate(request.prompt)
    input_prompt = prompts['fixed_prompt'] + user_prompt_en
    _eq.db_prompt_en(user_prompt_en, result_image_id)
    print(request.negative)
    user_negative_en = await api.deepl_translate(request.negative)
    _eq.db_negative_en(user_negative_en, result_image_id)
    input_negative = prompts['fixed_neg_prompt'] + user_negative_en
    
    # if request.negative != None:
    #     user_negative_en = await api.deepl_translate(request.negative)
    #     _eq.db_negative_en(user_negative_en, result_image_id)
    #     input_negative = prompts['fixed_neg_prompt'] + user_negative_en
    # else:
    #     input_negative = prompts['fixed_neg_prompt']
  
    image_urls = []
    bucket_name = AWS_BUCKET_NAME
            
    today = datetime.today().strftime('%Y%m%d')
    now = datetime.now().strftime('%H%M%S')
    counter_str = f"{counter:04d}"  
    subfolder = f"genai/i2i/{today}/{today}-{now}-{counter_str}"
    
    _eq.gen_processing(result_image_id)
    print('===================debug=======================')
    print(input_img)
    print('===================+++++=======================')
    if request.model_choice == "Realistic":       
        imgs = i2i_pipe(
            prompt=input_prompt,
            negative_prompt=input_negative,
            image=input_img,
            num_inference_steps=request.num_inference_steps,
            guidance_scale=request.cfg_scale,
            width=request.width,
            height=request.height,
            strength=request.denoising_strength,
            generator = torch.Generator(device="cuda").manual_seed(request.seed),
            # seed=request.seed,
            # padding_mask_crop=32, # same effect as “Only masked” area inpainting
            num_images_per_prompt=request.batch_count,
            result_image_id=result_image_id
        ).images
    
        # del imgs
        # torch.cuda.empty_cache()
        
    else:
        raise ValueError("Unsupported model choice")
    
    if imgs is None or not imgs:
            raise ValueError("Image generation returned no images.")
        
    for img in imgs:
        img_path = await _dl.save_image(img, output_dir)
        image_url = await _dl.upload_to_temp_s3(img_path, bucket_name, subfolder)
        image_urls.append(image_url)
        counter += 1
        
    return I2IResponse(prompt=input_prompt, image_urls=image_urls, seed=request.seed)
