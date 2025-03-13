from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class ScraperLog(BaseModel):
    page_id: Optional[str] = None  # ID of the scraped page (if available)
    url: HttpUrl  # URL of the LinkedIn page
    scraped_at: datetime  # Timestamp of scraping
    status: str  # "success" or "failed"
    message: str  # General message about the scrape result
    error_message: Optional[str] = None  # Store errors if the scrape fails
