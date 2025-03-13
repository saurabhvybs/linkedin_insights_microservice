from fastapi import APIRouter
from .scraper import router as scraper_router
from .page import router as page_router

router = APIRouter()

router.include_router(scraper_router, prefix="/scraper", tags=["Scraper"])
router.include_router(page_router, prefix="/page", tags=["Page"])
