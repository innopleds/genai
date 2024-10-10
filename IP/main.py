import os
import boto3
import random
from fastapi.responses import HTMLResponse
from typing import Optional
from fastapi import FastAPI, HTTPException, Form, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from modules.generator import generate_ip_image
from modules.schemas import IPRequest, IPResponse

# import torch.multiprocessing as mp

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 허용할 출처 리스트
    allow_credentials=True,  # 쿠키 허용 여부
    allow_methods=["*"],  # 허용할 HTTP 메서드
    allow_headers=["*"],  # 허용할 HTTP 헤더
)


@app.post("/generate_ip", response_model=IPResponse)
async def generate_ip(
    model_choice: str = Form("Realistic"),
    prompt: str = Form(""),
    negative: str = Form(""),
    num_inference_steps: int = Form(30),
    width: int = Form(1080),
    height: int = Form(1080),
    cfg_scale: float = Form(10.0),
    denoising_strength: float = Form(1.0),
    batch_count: int = Form(1),
    seed: int = Form(3299299139),
    input_img: UploadFile = File(...),
    mask_img: UploadFile = File(...)
):
    if seed is None:
        seed = random.randint(0, 2**32 - 1)

    try:
        input_img_path = os.path.join("input_images", input_img.filename)
        os.makedirs("input_images", exist_ok=True)
        mask_img_path = os.path.join("mask_images", mask_img.filename)
        os.makedirs("mask_images", exist_ok=True)
        
        with open(input_img_path, "wb") as f:
            f.write(await input_img.read())
        with open(mask_img_path, "wb") as f:
            f.write(await mask_img.read())
            

        request = IPRequest(
            model_choice=model_choice,
            prompt=prompt,
            negative=negative,
            num_inference_steps=num_inference_steps,
            width=width,
            height=height,
            cfg_scale=cfg_scale,
            denoising_strength=denoising_strength,
            batch_count=batch_count,
            seed=seed
        )
        
        response = await generate_ip_image(request, input_img_path, mask_img_path, output_dir="generated_images")
        
        ##########################################################################################
        # request_data = (request, input_img_path, mask_img_path, "generated_images")
        # p = mp.Process(target=process_request, args=(request_data,))
        # p.start()
        # p.join()

        # # 여기서 프로세스의 결과를 처리하여 응답으로 반환합니다.
        # response = process_request(request_data)  # 동기 방식으로 호출하여 결과 얻기
        ##########################################################################################
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/save")
async def save_image(
    source_url: str = Form(...)
):
    try:
        if not source_url.startswith("https://"):
            raise HTTPException(status_code=400, detail="Invalid URL format")
        
        bucket_name = source_url.split(".s3.amazonaws.com/")[0].replace("https://", "")
        source_key = source_url.split(".s3.amazonaws.com/")[1]
        
        if not source_key.startswith("genai/"):
            raise HTTPException(status_code=400, detail="Invalid source key format")
        
        relative_path = source_key[len("genai/"):]
        destination_key = f"genai_save/{relative_path}"
        
        s3 = boto3.client("s3")
        copy_source = {'Bucket': bucket_name, 'Key': source_key}

        s3.copy_object(CopySource=copy_source, Bucket=bucket_name, Key=destination_key)
        
        return {"message": "Image saved successfully", "new_url": f"https://{bucket_name}.s3.amazonaws.com/{destination_key}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # mp.set_start_method('spawn')  # 필요한 경우 start method 설정
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860, reload=True)
    asyncio.run(generate_ip_image())
