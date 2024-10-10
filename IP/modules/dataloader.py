import json
from PIL import Image
import os
import uuid
import boto3

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