from pydantic import BaseModel
from typing import Optional, List
from PIL import Image
# from fastapi import Form, UploadFile, File


class IPRequest(BaseModel):
    model_choice: str = "Realistic"
    prompt: str
    negative: Optional[str] 
    num_inference_steps: int = 40
    width: int = 512
    height: int = 512
    cfg_scale: float = 7.5
    denoising_strength: float = 0.7
    batch_count: int = 1
    seed: Optional[int] = 3299299139

class IPResponse(BaseModel):
    prompt: str
    image_urls: List[str]
    seed: int




