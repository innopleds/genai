from pydantic import BaseModel
from typing import Optional, List
# from fastapi import Form, UploadFile, File

class T2IRequest(BaseModel):
    model_choice: str
    prompt: str
    negative: Optional[str]
    num_inference_steps: int
    width: int 
    height: int 
    cfg_scale: float
    batch_count: int 
    seed: Optional[int] 
    # keyword_api: bool = Form(False)

class T2IResponse(BaseModel):
    prompt: str
    image_urls: List[str]
