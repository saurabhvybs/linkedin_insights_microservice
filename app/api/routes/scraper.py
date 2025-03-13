from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
from dotenv import load_dotenv
import time
from datetime import datetime
from app.core.database import scraper_collection
from typing import Optional, Dict, Any, List
from bson import ObjectId

router = APIRouter()

# Load environment variables
load_dotenv()
SESSION_COOKIE = os.getenv("LI_AT")

class ScrapeRequest(BaseModel):
    url: HttpUrl
    type: str = "company"  # Default to company, can be "company", "profile", or "post"
    page_id: Optional[str] = None  # Optional ID of the LinkedIn page

class ScraperLog(BaseModel):
    page_id: Optional[str] = None  # ID of the scraped page (if available)
    url: str  # URL of the LinkedIn page as string, not HttpUrl
    scraped_at: datetime  # Timestamp of scraping
    status: str  # "success" or "failed"
    message: str  # General message about the scrape result
    error_message: Optional[str] = None  # Store errors if the scrape fails
    data: Optional[Dict[str, Any]] = None  # The actual scraped data
    type: str  # Store the type of scrape (company, profile, post)
    
    class Config:
        arbitrary_types_allowed = True

@router.post("/scrape")
async def scrape_linkedin_page(request: ScrapeRequest):
    if not SESSION_COOKIE:
        raise HTTPException(status_code=500, detail="Missing LinkedIn session cookie")

    # Create a scraper log entry - convert HttpUrl to string
    scraper_log = ScraperLog(
        page_id=request.page_id,
        url=str(request.url),  # Convert HttpUrl to string
        scraped_at=datetime.now(),
        status="pending",
        message="Scraping in progress",
        type=request.type  # Store the page type
    )

    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")

    # Initialize Selenium WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Add LinkedIn session cookie
        driver.get("https://www.linkedin.com")
        driver.add_cookie({"name": "li_at", "value": SESSION_COOKIE, "domain": ".linkedin.com"})
        
        # Now navigate to the target page
        driver.get(str(request.url))
        
        # Wait for page to load - more sophisticated wait
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Scroll down to load dynamic content
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(3)
        
        # Choose scraping method based on page type
        if request.type == "company":
            data = scrape_company_page(driver)
        elif request.type == "profile":
            data = scrape_profile_page(driver)
        elif request.type == "post":
            data = scrape_post_page(driver)
        else:
            data = {"error": "Invalid page type specified"}
        
        # Update the scraper log with results
        if "error" in data:
            scraper_log.status = "failed"
            scraper_log.message = "Failed to scrape page completely"
            scraper_log.error_message = data["error"]
            del data["error"]  # Remove error from data before storing
        else:
            scraper_log.status = "success"
            scraper_log.message = f"Successfully scraped {request.type} page"
        
        # Add the scraped data to the log
        # Include the type in the data for better filtering
        data["page_type"] = request.type
        scraper_log.data = data
        
        # Convert ScraperLog to a plain dictionary for MongoDB storage
        scraper_log_dict = scraper_log.dict()
        
        # Store the scraper log in MongoDB
        try:
            result = await scraper_collection.insert_one(scraper_log_dict)
            print(f"MongoDB insertion result: {result.acknowledged}, ID: {result.inserted_id}")
            
            if not result.acknowledged:
                raise Exception("MongoDB did not acknowledge the insertion")
                
            # Return response with scraped data and log ID
            return {
                "status": scraper_log.status,
                "message": scraper_log.message,
                "log_id": str(result.inserted_id),
                "data": data
            }
        except Exception as db_error:
            raise HTTPException(
                status_code=500, 
                detail=f"Database error: {str(db_error)}"
            )

    except Exception as e:
        # Update scraper log with error information
        scraper_log.status = "failed"
        scraper_log.message = "Exception during scraping"
        scraper_log.error_message = str(e)
        
        # Still try to save the log
        try:
            # Convert to dict before saving
            scraper_log_dict = scraper_log.dict()
            result = await scraper_collection.insert_one(scraper_log_dict)
            print(f"Error log insertion result: {result.acknowledged}, ID: {result.inserted_id}")
        except Exception as mongo_error:
            # Return both the original error and the MongoDB error
            return {
                "status": "error",
                "detail": f"Scraping error: {str(e)}. Database error: {str(mongo_error)}"
            }
            
        return {
            "status": "error", 
            "detail": str(e)
        }
    finally:
        driver.quit()

def scrape_company_page(driver):
    """Extract data from a LinkedIn company page"""
    data = {
        "page": {
            "name": "",
            "industry": "",
            "website": "",
            "company_size": "",
            "headquarters": "",
            "founded": "",
            "specialties": []
        },
        "about": "",
        "recent_posts": []
    }
    
    try:
        # Company name
        try:
            name_element = driver.find_element(By.CLASS_NAME, "org-top-card-summary__title")
            data["page"]["name"] = name_element.text.strip()
        except:
            pass
        
        # Industry and other company info
        try:
            info_items = driver.find_elements(By.CLASS_NAME, "org-top-card-summary-info-list__info-item")
            if info_items:
                data["page"]["industry"] = info_items[0].text.strip()
                
            # More detailed company information
            details = driver.find_elements(By.CLASS_NAME, "org-about-company-module__about-us-item")
            for detail in details:
                label = detail.find_element(By.CLASS_NAME, "org-about-company-module__about-us-label").text.strip().lower()
                value = detail.find_element(By.CLASS_NAME, "org-about-company-module__about-us-text").text.strip()
                
                if "website" in label:
                    data["page"]["website"] = value
                elif "size" in label:
                    data["page"]["company_size"] = value
                elif "headquarters" in label:
                    data["page"]["headquarters"] = value
                elif "founded" in label:
                    data["page"]["founded"] = value
                elif "specialties" in label:
                    data["page"]["specialties"] = [s.strip() for s in value.split(",")]
        except:
            pass
            
        # About section
        try:
            about_section = driver.find_element(By.CLASS_NAME, "org-about-us-organization-description__text")
            data["about"] = about_section.text.strip()
        except:
            pass
            
        # Recent posts
        try:
            posts = driver.find_elements(By.CLASS_NAME, "occludable-update")
            for i, post in enumerate(posts[:3]):  # Get first 3 posts
                try:
                    post_data = {
                        "text": post.find_element(By.CLASS_NAME, "feed-shared-update-v2__description").text.strip(),
                        "engagement": {}
                    }
                    
                    # Try to get engagement metrics
                    try:
                        metrics = post.find_elements(By.CLASS_NAME, "social-details-social-counts__item")
                        for metric in metrics:
                            count_text = metric.text.strip().lower()
                            if "like" in count_text:
                                post_data["engagement"]["likes"] = count_text
                            elif "comment" in count_text:
                                post_data["engagement"]["comments"] = count_text
                    except:
                        pass
                        
                    data["recent_posts"].append(post_data)
                except:
                    continue
        except:
            pass
            
    except Exception as e:
        data["error"] = str(e)
        
    return data

def scrape_profile_page(driver):
    """Extract data from a LinkedIn user profile page"""
    data = {
        "user": {
            "name": "",
            "headline": "",
            "location": "",
            "connections": "",
            "about": ""
        },
        "experience": [],
        "education": []
    }
    
    try:
        # Basic profile information
        try:
            data["user"]["name"] = driver.find_element(By.CLASS_NAME, "text-heading-xlarge").text.strip()
            data["user"]["headline"] = driver.find_element(By.CLASS_NAME, "text-body-medium").text.strip()
            
            location_element = driver.find_element(By.CSS_SELECTOR, ".pv-text-details__left-panel .text-body-small")
            data["user"]["location"] = location_element.text.strip()
            
            connections_element = driver.find_element(By.CSS_SELECTOR, ".pv-text-details__right-panel .text-body-small")
            data["user"]["connections"] = connections_element.text.strip()
        except:
            pass
            
        # About section
        try:
            about_section = driver.find_element(By.ID, "about")
            about_text = about_section.find_element(By.XPATH, "./following-sibling::div[1]//span")
            data["user"]["about"] = about_text.text.strip()
        except:
            pass
            
        # Experience section
        try:
            experience_section = driver.find_element(By.ID, "experience")
            experience_items = experience_section.find_elements(By.XPATH, "./following-sibling::div[1]//li")
            
            for item in experience_items:
                try:
                    exp = {
                        "title": item.find_element(By.CLASS_NAME, "t-bold").text.strip(),
                        "company": item.find_element(By.CLASS_NAME, "t-normal").text.strip(),
                        "duration": item.find_elements(By.CLASS_NAME, "t-normal")[1].text.strip() if len(item.find_elements(By.CLASS_NAME, "t-normal")) > 1 else ""
                    }
                    data["experience"].append(exp)
                except:
                    continue
        except:
            pass
            
        # Education section
        try:
            education_section = driver.find_element(By.ID, "education")
            education_items = education_section.find_elements(By.XPATH, "./following-sibling::div[1]//li")
            
            for item in education_items:
                try:
                    edu = {
                        "school": item.find_element(By.CLASS_NAME, "t-bold").text.strip(),
                        "degree": item.find_element(By.CLASS_NAME, "t-normal").text.strip() if item.find_elements(By.CLASS_NAME, "t-normal") else "",
                        "years": item.find_elements(By.CLASS_NAME, "t-normal")[1].text.strip() if len(item.find_elements(By.CLASS_NAME, "t-normal")) > 1 else ""
                    }
                    data["education"].append(edu)
                except:
                    continue
        except:
            pass
            
    except Exception as e:
        data["error"] = str(e)
        
    return data

def scrape_post_page(driver):
    """Extract data from a LinkedIn post page"""
    data = {
        "post": {
            "author": "",
            "author_headline": "",
            "content": "",
            "timestamp": "",
            "engagement": {
                "likes": "",
                "comments": "",
                "reposts": ""
            }
        },
        "comments": []
    }
    
    try:
        # Post author
        try:
            author_element = driver.find_element(By.CLASS_NAME, "feed-shared-actor__name")
            data["post"]["author"] = author_element.text.strip()
            
            headline_element = driver.find_element(By.CLASS_NAME, "feed-shared-actor__description")
            data["post"]["author_headline"] = headline_element.text.strip()
            
            timestamp_element = driver.find_element(By.CLASS_NAME, "feed-shared-actor__sub-description")
            data["post"]["timestamp"] = timestamp_element.text.strip()
        except:
            pass
            
        # Post content
        try:
            content_element = driver.find_element(By.CLASS_NAME, "feed-shared-update-v2__description")
            data["post"]["content"] = content_element.text.strip()
        except:
            pass
            
        # Engagement metrics
        try:
            metrics = driver.find_elements(By.CLASS_NAME, "social-details-social-counts__item")
            for metric in metrics:
                count_text = metric.text.strip().lower()
                if "like" in count_text:
                    data["post"]["engagement"]["likes"] = count_text
                elif "comment" in count_text:
                    data["post"]["engagement"]["comments"] = count_text
                elif "repost" in count_text:
                    data["post"]["engagement"]["reposts"] = count_text
        except:
            pass
            
        # Comments
        try:
            comments = driver.find_elements(By.CLASS_NAME, "comments-comment-item")
            for i, comment in enumerate(comments[:5]):  # Get first 5 comments
                try:
                    comment_data = {
                        "author": comment.find_element(By.CLASS_NAME, "comments-post-meta__name-text").text.strip(),
                        "text": comment.find_element(By.CLASS_NAME, "comments-comment-item__main-content").text.strip()
                    }
                    data["comments"].append(comment_data)
                except:
                    continue
        except:
            pass
            
    except Exception as e:
        data["error"] = str(e)
        
    return data

# Additional endpoints to retrieve scraped data

@router.get("/logs")
async def get_scraper_logs(limit: int = 10, skip: int = 0):
    """Get recent scraper logs with pagination"""
    logs = await scraper_collection.find().sort("scraped_at", -1).skip(skip).limit(limit).to_list(limit)
    # Convert ObjectId to string for JSON serialization
    for log in logs:
        log["_id"] = str(log["_id"])
    return {"logs": logs}

@router.get("/logs/{log_id}")
async def get_scraper_log(log_id: str):
    """Get a specific scraper log by ID"""
    try:
        log = await scraper_collection.find_one({"_id": ObjectId(log_id)})
        if log:
            log["_id"] = str(log["_id"])
            return log
        else:
            raise HTTPException(status_code=404, detail="Log not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid log ID: {str(e)}")

@router.get("/data/{type}")
async def get_scraped_data_by_type(type: str, limit: int = 10, skip: int = 0):
    """Get scraped data by type (company, profile, post)"""
    # Updated query to look for the type field at the top level
    logs = await scraper_collection.find(
        {"status": "success", "type": type}
    ).sort("scraped_at", -1).skip(skip).limit(limit).to_list(limit)
    
    for log in logs:
        log["_id"] = str(log["_id"])
    
    return {"data": logs}