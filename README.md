# LinkedIn Insights Microservice

## 📌 Overview
This microservice scrapes LinkedIn company pages and extracts insights such as company details, recent posts, and engagement metrics. It provides a RESTful API built with **FastAPI**, utilizes **MongoDB** for data storage, and supports **asynchronous processing** for efficient scraping.

---

## 🚀 Features
- **Scrape LinkedIn company pages**
- **Extract key insights** (company info, posts, engagement stats)
- **Store data in MongoDB**
- **FastAPI-based RESTful API** with endpoints for filtering and pagination
- **Redis integration (if applicable)** for caching
- **Support for environment variables (.env)**

---

## 🏗 Project Structure
```
linkedin_insights_microservice/
│-- app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── scraper.py   # Scraper API routes
│   │   │   ├── page.py      # Page API routes
│   ├── core/
│   │   ├── database.py      # MongoDB connection
│   │   ├── config.py        # Configuration settings
│   ├── main.py              # FastAPI entry point
│-- .env                      # Environment variables
│-- requirements.txt          # Python dependencies
│-- README.md                 # Project documentation
```

---

## ⚙️ Setup & Installation
### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/your-repo/linkedin_insights_microservice.git
cd linkedin_insights_microservice
```

### **2️⃣ Create & Activate Virtual Environment**
```bash
python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows
```

### **3️⃣ Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4️⃣ Set Up Environment Variables**
Create a `.env` file in the project root and add:
```
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=linked_microservice_insights
```

### **5️⃣ Start the FastAPI Server**
```bash
uvicorn app.main:app --reload
```

The API will be available at: [http://localhost:8000](http://localhost:8000)

---

## 📡 API Endpoints
### **1️⃣ Scrape LinkedIn Company Page**
```http
POST /api/scraper/scrape
```
**Request Body:**
```json
{
  "url": "https://www.linkedin.com/company/microsoft",
  "type": "company"
}
```
**Response:**
```json
{
  "status": "success",
  "message": "Successfully scraped company page",
  "data": { ... }
}
```

### **2️⃣ Fetch All Scraped Pages**
```http
GET /api/pages
```

### **3️⃣ Fetch a Specific Page by ID**
```http
GET /api/pages/{page_id}
```

---

## 🛠 Debugging Common Issues
### **1️⃣ Module Not Found: `database`**
- Ensure you are using **absolute imports** in `scraper.py`:
  ```python
  from app.core.database import pages_collection
  ```

### **2️⃣ MongoDB Connection Issues**
- Ensure MongoDB is running:
  ```bash
  mongod --dbpath /path/to/data/db
  ```
- Verify your `.env` file has the correct `MONGO_URI`

### **3️⃣ Server Not Starting (`Address already in use`)**
- Kill the existing process using port 8000:
  ```bash
  lsof -i :8000  # Find process ID
  kill -9 <PID>  # Kill process
  ```

---

## 📜 License
This project is licensed under the **MIT License**.

---

## 🤝 Contributing
Contributions are welcome! Feel free to open issues or submit pull requests.

Happy coding! 🚀