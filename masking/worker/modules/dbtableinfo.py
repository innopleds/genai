from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session, select
import json
import datetime

class imagetable_info(SQLModel, table=True):
    id: str = Field(default=None, primary_key=True)
    user_id: str
    url: str
    prompt_ko: str
    negative_ko: Optional[str]
    info: json
    progress: int
    status: str
    error: Optional[str]
    prompt_en: str
    negative_en: Optional[str]
#    created_at: datetime
#    updated_at: datetime
    gen_type: str
    input_img: str
    mask_img: str
