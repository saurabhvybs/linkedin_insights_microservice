from fastapi import FastAPI
from app.api.routes.page import router as page_router
from app.api.routes.post import router as post_router
from app.api.routes.user import router as user_router
from app.api.routes.scraper import router as scraper_router
from app.core.database import scraper_collection, check_mongo_connection

app = FastAPI(
    title="LinkedIn Insights Microservice",
    description="A microservice to scrape and retrieve LinkedIn page insights",
    version="1.0.0"
)

# Run MongoDB connection check on startup
@app.on_event("startup")
async def startup_event():
    await check_mongo_connection()

# Registering the routers
app.include_router(page_router, prefix="/api/pages", tags=["Pages"])
app.include_router(post_router, prefix="/api/posts", tags=["Posts"])
app.include_router(user_router, prefix="/api/users", tags=["Users"])
app.include_router(scraper_router, prefix="/api/scraper", tags=["Scraper"])

@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to LinkedIn Insights Microservice!"}

# Fetch scraped data
@app.get("/scraped_data", tags=["Scraper"])
async def get_scraped_data():
    data = await scraper_collection.find().to_list(100)  
    return {"scraped_data": data}


@app.on_event("shutdown")
async def shutdown():
    await close_mongo_connection()
