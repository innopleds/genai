import json
from PIL import Image
import os
import uuid
import boto3
from fastapi import FastAPI, HTTPException
from io import BytesIO

async def load_json(path):
    try:
        with open(path, 'r') as json_file:
            prompts = json.load(json_file)
            print("JSON data loaded successfully")
            
    except FileNotFoundError:
        print("The file a.json does not exist")
    except json.JSONDecodeError:
        print("Error decoding JSON from the file")
    return prompts


async def save_image(img: Image, output_dir: str) -> str:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    img_id = str(uuid.uuid4())
    img_path = os.path.join(output_dir, f"{img_id}.png")
    img.save(img_path)
    return img_path

async def upload_to_temp_s3(img_path: str, bucket_name: str, subfolder: str) -> str:
    s3 = boto3.client("s3")
    s3_key = f"{subfolder}/{os.path.basename(img_path)}"
    s3.upload_file(img_path, bucket_name, s3_key)
    return f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"

def load_image(image_url):
    s3 = boto3.client("s3")

    if image_url.startswith('https://'):
        try:
            #'https://bucket-name.s3.region.amazonaws.com/object-key'
            s3_url_parts = image_url.replace("https://", "").split(".s3.")
            bucket_name = s3_url_parts[0]  # 버킷 
            object_key = image_url.split(".amazonaws.com/")[1]  

            
            s3_response = s3.get_object(Bucket=bucket_name, Key=object_key)
            image_data = s3_response['Body'].read()
        
            input_image = Image.open(BytesIO(image_data)).convert("RGB")
            return input_image

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error downloading image from S3: {str(e)}")
    else:
        raise HTTPException(status_code=400, detail="Invalid image URL format. Only HTTPS S3 URLs are supported.")
