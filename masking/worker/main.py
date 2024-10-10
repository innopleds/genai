import base64
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import asyncio
import random

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from modules.queue import sqs_dequeue
from modules.generator import generate_ip_image
from modules.schemas import IPRequest
import modules.exe_query as _eq
from modules.dataloader import load_image

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 허용할 출처 리스트
    allow_credentials=True,  # 쿠키 허용 여부
    allow_methods=["*"],  # 허용할 HTTP 메서드
    allow_headers=["*"],  # 허용할 HTTP 헤더
)
async def generate_ip(result_image_id):
    print("image_id: ", result_image_id)

    df = _eq.get_param_info(result_image_id)
    # if input_img.startswith('data:image/png;base64,'):
    #     input_img = input_img[len('data:image/png;base64,'):]   
    # if mask_img.startswith('data:image/png;base64,'):
    #     mask_img = mask_img[len('data:image/png;base64,'):]
    input_img_result = _eq.input_img(result_image_id)
    input_img_url = input_img_result[0] 
    print("HERE",input_img_url)
    mask_img_result = _eq.mask_img(result_image_id)
    mask_img_url = mask_img_result[0]

    
    try:
        request = IPRequest(
            model_choice=df['theme'][0],
            prompt=df['prompt'][0],
            negative=df['negative'][0],
            num_inference_steps=30,
            width=df['width'][0],
            height=df['height'][0],
            cfg_scale=df['cfgscale'][0],
            denoising_strength=df['denoising'][0],
            batch_count=1,
            seed =random.randint(0, 2**32 - 1)
            
        )
        print(request.seed)
        seed_value=str(request.seed)
        input_image = load_image(input_img_url)
        mask_image = load_image(mask_img_url)
        try:
            response = await generate_ip_image(request, result_image_id, input_image, mask_image, output_dir="generated_images")
        except Exception as e:
            err_msg = str(e)
            _eq.error_msg(err_msg, result_image_id)
        image_urls = response.image_urls[0]
        _eq.gen_completed(image_urls, result_image_id, seed_value)
        
        return response

    except Exception as e:
        err_msg = str(e)
        _eq.error_msg(err_msg, result_image_id)
        raise HTTPException(status_code=500, detail=str(e))

async def process_queue():
    while True:
        try:
            result_image_id = await sqs_dequeue()
            if result_image_id:
                await generate_ip(result_image_id)
            else:
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Error processing queue: {e}")
            await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(process_queue())
