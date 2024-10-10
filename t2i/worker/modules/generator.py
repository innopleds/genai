import os
from datetime import datetime
from dotenv import load_dotenv
import torch

from modules.model import load_models
from modules.schemas import T2IRequest, T2IResponse 
import modules.externel_api as api
import modules.dataloader as _dl
import modules.exe_query as _eq

load_dotenv('')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')

t2i_pipe, refiner = load_models()
counter = 1

async def generate_t2i_image(request: T2IRequest, result_image_id, output_dir: str) -> T2IResponse:
    global counter

    
    prompts = await _dl.load_json('./fixed_prompt.json')
    
    user_prompt_en = await api.deepl_translate(request.prompt)
    input_prompt = prompts['fixed_prompt'] + user_prompt_en+ ", ultra high res, photorealistic, taken by canon EOS, intricate details,"
    
    _eq.db_prompt_en(user_prompt_en, result_image_id)
    
    if request.negative != None:
        user_negative_en = await api.deepl_translate(request.negative)
        _eq.db_negative_en(user_negative_en, result_image_id)
        input_negative = prompts['fixed_neg_prompt'] + user_negative_en+",blurry, cartoon, animated"
    else:
        input_negative = prompts['fixed_neg_prompt']+",blurry, cartoon, animated"
    
    image_urls = []
    bucket_name = AWS_BUCKET_NAME
    
    today = datetime.today().strftime('%Y%m%d')
    now = datetime.now().strftime('%H%M%S')
    counter_str = f"{counter:04d}"  
    subfolder = f"genai/t2i/{today}/{today}-{now}-{counter_str}"
    
    _eq.gen_processing(result_image_id)
    latent = None
    #print(t2i_pipe.scheduler.compatibles)
    try: 
        if request.model_choice == "Realistic":
            latent = t2i_pipe(
                prompt=input_prompt,
                negative_prompt=input_negative,
                num_inference_steps=request.num_inference_steps,
                guidance_scale=request.cfg_scale,
                width=request.width,
                height=request.height,
                # seed=request.seed,
                generator = torch.Generator(device="cuda").manual_seed(request.seed),
                num_images_per_prompt=request.batch_count,
                result_image_id=result_image_id
            ).images

            refined_images = refiner(
                prompt=input_prompt,
                negative_prompt=input_negative,
                num_inference_steps=request.num_inference_steps,
                guidance_scale=request.cfg_scale,
                width=request.width,
                height=request.height,
                generator = torch.Generator(device="cuda").manual_seed(request.seed),
                num_images_per_prompt=request.batch_count,
                result_image_id=result_image_id,
                image=latent
              ).images

            for img in refined_images:
                img_path = await _dl.save_image(img, output_dir)
                if not img_path:
                    raise ValueError("Failed to save the generated image.")
                image_url = await _dl.upload_to_temp_s3(img_path, bucket_name, subfolder)
                if not image_url:
                    raise ValueError("Failed to upload the image to S3.")
                image_urls.append(image_url)
    
                counter += 1
            return T2IResponse(prompt=input_prompt, image_urls=image_urls)
        else:
            _eq.error_msg('Unsupported model choice', result_image_id)
        
        
    except Exception as e:
        err_msg = str(e)
        _eq.error_msg(err_msg, result_image_id)

    # if latent is None or not latent:
    #     raise ValueError("Image generation returned no images.")

    



#########################
###### ChatGPT API ######
#########################
# def input_prompts(gpt_api, prompts, prompt: str) -> str:
#     if gpt_api==False:
#         input_prompt = prompts['fixed_prompt'] + api.deepl_translate(prompt)
#     else:
#         print('gpt_api')
#         # input_prompt = prompts['fixed_prompt'] + api.gen_keyword(prompt)
            
#     return input_prompt


  # if request.keyword_api==False:
    #     input_prompt = prompts['fixed_prompt'] + api.deepl_translate(request.prompt)
    # else:
    #     print('gpt_api')