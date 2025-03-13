from fastapi import APIRouter, HTTPException
from app.core.database import pages_collection
from app.models.page import PageBase, PageCreate

router = APIRouter()


@router.post("/", summary="Create a new LinkedIn Page")
async def create_page(page: PageCreate):
    existing_page = await pages_collection.find_one({"page_id": page.page_id})
    if existing_page:
        raise HTTPException(status_code=400, detail="Page with this ID already exists")

    new_page = page.model_dump()
    await pages_collection.insert_one(new_page)
    return {"message": "Page created successfully", "page": new_page}


@router.get("/{page_id}", summary="Get LinkedIn Page details")
async def get_page(page_id: str):
    page = await pages_collection.find_one({"page_id": page_id})
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"page": page}


@router.put("/{page_id}", summary="Update LinkedIn Page")
async def update_page(page_id: str, updated_data: PageBase):
    page = await pages_collection.find_one({"page_id": page_id})
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    await pages_collection.update_one({"page_id": page_id}, {"$set": updated_data.model_dump()})
    return {"message": "Page updated successfully"}


@router.delete("/{page_id}", summary="Delete LinkedIn Page")
async def delete_page(page_id: str):
    page = await pages_collection.find_one({"page_id": page_id})
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")

    await pages_collection.delete_one({"page_id": page_id})
    return {"message": "Page deleted successfully"}
