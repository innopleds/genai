import hashlib
import base64
from PIL import Image
from io import BytesIO
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from diffusers import StableDiffusionInpaintPipeline, DPMSolverMultistepScheduler,AutoencoderKL
import torch
import io


def compute_image_hash(image):
    hasher = hashlib.sha256()
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    hasher.update(buffer.getvalue())
    return hasher.hexdigest()
dpm = DPMSolverMultistepScheduler(
    beta_start=0.00085,
    beta_end=0.012,
    beta_schedule="scaled_linear"
)

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
load_dotenv()
pipe = load_models()

db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_pwd = os.getenv('DB_PWD')

url = f'postgresql://{db_user}:{db_pwd}@{db_host}/postgres'
engine = create_engine(url)
Session = sessionmaker(bind=engine)

session = Session()

result_image_id = '399d34ad-623b-411f-8e89-c692b04206b3'

input_img_query = text("""
    SELECT input_img
    FROM image
    WHERE id = :result_image_id
    """)
input_img_result = session.execute(input_img_query, {'result_image_id': result_image_id}).fetchone()
session.commit()
    
input_base64_data = input_img_result[0].split(",")[1]
input_image = Image.open(BytesIO(base64.b64decode(input_base64_data)))

mask_img_query = text("""
    SELECT mask_img
    FROM image
    WHERE id = :result_image_id
    """)
mask_img_result = session.execute(mask_img_query, {'result_image_id': result_image_id}).fetchone()
session.commit()

  
input_base64_data = input_img_result[0].split(",")[1]
input_image = Image.open(BytesIO(base64.b64decode(input_base64_data))).convert("RGB")

mask_base64_data = mask_img_result[0].split(",")[1]
mask_image = Image.open(BytesIO(base64.b64decode(mask_base64_data))).convert("L")

input_image.save("test_input.png")
print(f'Input image size: {input_image.size}')
mask_image.save("test_mask.png")
print(f'Mask image size: {mask_image.size}')

test = Image.open("./input_images/test_input.png")

if compute_image_hash(input_image) == compute_image_hash(test):
    print("Images are the same.")
else:
    print("Images are different.")



imgs = pipe(prompt="수분감 넘치는 배경",
            negative_prompt="input_negative",
            image=input_image,
            mask_image=mask_image,
            num_inference_steps=20,
            guidance_scale=15,
            width=1080,
            height=1080,
            strength=0.8,
            generator = torch.Generator(device="cuda").manual_seed(45645),
            # seed=request.seed,
            # padding_mask_crop=16, # same effect as “Only masked” area inpainting
            num_images_per_prompt=1
        ).images

imgs.save("result.png")