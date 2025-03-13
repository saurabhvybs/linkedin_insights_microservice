from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from pydantic import Field

class PostBase(BaseModel):
    page_id: str
    post_id: str
    content: Optional[str] = None
    likes: int = 0
    comments_count: int = 0
    shares: int = 0
    created_at: datetime

class PostCreate(PostBase):
    pass  # Used for inserting new posts

class PostDB(PostBase):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")

    class Config:
        orm_mode = True
        from_attributes = True
