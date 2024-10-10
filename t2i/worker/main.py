import asyncio
import random
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from modules.queue import sqs_dequeue  
from modules.schemas import T2IRequest
from modules.generator import generate_t2i_image
import modules.exe_query as _eq

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 허용할 출처 리스트
    allow_credentials=True,  # 쿠키 허용 여부
    allow_methods=["*"],  # 허용할 HTTP 메서드
    allow_headers=["*"],  # 허용할 HTTP 헤더s
)

async def generate_image(result_image_id):
    print("image_id: ", result_image_id)
    
    df = _eq.get_param_info(result_image_id)
    try:
        request = T2IRequest(
            model_choice=df['theme'][0],
            prompt=df['prompt'][0],
            negative=df['negative'][0],
            num_inference_steps=30,
            width=df['width'][0],
            height=df['height'][0],
            cfg_scale=df['cfgscale'][0],
            batch_count=1,
            seed=random.randint(0, 2**32 - 1)
        )
        response = await generate_t2i_image(request, result_image_id, output_dir="generated_images")
        image_urls = response.image_urls[0]
        seed_value=str(request.seed)
        _eq.gen_completed(image_urls, result_image_id,seed_value)

        return response
    
    except Exception as e:
        err_msg = str(e)
        _eq.error_msg(err_msg, result_image_id)

async def process_queue():
    while True:
        try:
            result_image_id = await sqs_dequeue()
            if result_image_id:
                await generate_image(result_image_id)
            else:
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Error processing queue: {e}")
            await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    loop.create_task(process_queue())

