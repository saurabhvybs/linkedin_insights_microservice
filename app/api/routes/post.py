from fastapi import APIRouter, HTTPException, Query
from app.core.database import posts_collection
from app.models.post import PostCreate, PostDB
from typing import List

router = APIRouter()


@router.get("/{post_id}", summary="Get LinkedIn Post details")
async def get_post(post_id: str):
    post = await posts_collection.find_one({"post_id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"post": post}


@router.get("/", summary="Get all LinkedIn Posts")
async def get_all_posts(
    skip: int = Query(0, description="Number of posts to skip"),
    limit: int = Query(10, description="Number of posts to retrieve")
):
    posts = await posts_collection.find().skip(skip).limit(limit).to_list(length=limit)
    return {"posts": posts}


@router.post("/", summary="Create a new LinkedIn Post")
async def create_post(post: PostCreate):
    existing_post = await posts_collection.find_one({"post_id": post.post_id})
    if existing_post:
        raise HTTPException(status_code=400, detail="Post with this ID already exists")

    new_post = post.model_dump()
    await posts_collection.insert_one(new_post)
    return {"message": "Post created successfully", "post": new_post}


@router.put("/{post_id}", summary="Update LinkedIn Post")
async def update_post(post_id: str, updated_data: PostCreate):
    post = await posts_collection.find_one({"post_id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    await posts_collection.update_one({"post_id": post_id}, {"$set": updated_data.model_dump(exclude_unset=True)})
    return {"message": "Post updated successfully"}


@router.delete("/{post_id}", summary="Delete LinkedIn Post")
async def delete_post(post_id: str):
    post = await posts_collection.find_one({"post_id": post_id})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    await posts_collection.delete_one({"post_id": post_id})
    return {"message": "Post deleted successfully"}
