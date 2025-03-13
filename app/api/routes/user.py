from fastapi import APIRouter, HTTPException
from app.core.database import users_collection
from app.models.user import UserCreate, UserBase

router = APIRouter()


@router.post("/", summary="Create a new user")
async def create_user(user: UserCreate):
    existing_user = await users_collection.find_one({"linkedin_id": user.linkedin_id})
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this LinkedIn ID already exists")

    new_user = user.model_dump()
    await users_collection.insert_one(new_user)
    return {"message": "User created successfully", "user": new_user}


@router.get("/{linkedin_id}", summary="Get user details")
async def get_user(linkedin_id: str):
    user = await users_collection.find_one({"linkedin_id": linkedin_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {"user": user}


@router.put("/{linkedin_id}", summary="Update user details")
async def update_user(linkedin_id: str, updated_data: UserBase):
    user = await users_collection.find_one({"linkedin_id": linkedin_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await users_collection.update_one({"linkedin_id": linkedin_id}, {"$set": updated_data.model_dump()})
    return {"message": "User updated successfully"}


@router.delete("/{linkedin_id}", summary="Delete a user")
async def delete_user(linkedin_id: str):
    user = await users_collection.find_one({"linkedin_id": linkedin_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await users_collection.delete_one({"linkedin_id": linkedin_id})
    return {"message": "User deleted successfully"}
