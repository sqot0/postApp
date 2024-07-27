from pydantic import BaseModel
from datetime import datetime

class Post(BaseModel):
    id: int
    title: str
    content: str
    published: datetime
    author: int

    class Config:
        orm_mode = True

class PostCreate(BaseModel):
    title: str
    content: str