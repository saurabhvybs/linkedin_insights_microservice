from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class PageBase(BaseModel):
    page_id: str  
    name: str
    url: HttpUrl
    profile_picture: Optional[HttpUrl] = None
    description: Optional[str] = None
    website: Optional[HttpUrl] = None
    industry: Optional[str] = None
    followers: Optional[int] = None
    head_count: Optional[int] = None
    specialities: Optional[List[str]] = None

class PageCreate(PageBase):
    pass  # Used for inserting new pages

class PageDB(PageBase):
    id: str  #ObjectId

    class Config:
        orm_mode = True
        from_attributes = True
