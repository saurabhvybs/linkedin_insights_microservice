from pydantic import BaseModel, HttpUrl
from typing import Optional

class UserBase(BaseModel):
    linkedin_id: str  # Unique LinkedIn user ID
    name: str
    profile_url: HttpUrl
    profile_picture: Optional[HttpUrl] = None
    job_title: Optional[str] = None
    company: Optional[str] = None

class UserCreate(UserBase):
    pass  # Used for inserting new users

class UserDB(UserBase):
    id: str  #ObjectId

    class Config:
        orm_mode = True
        from_attributes = True
