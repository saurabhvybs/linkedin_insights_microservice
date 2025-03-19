# Single FROM statement with platform specification
FROM --platform=linux/amd64 python:3.13

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Chrome & Chromedriver for Selenium
RUN apt-get update && apt-get install -y wget unzip curl gnupg \
    && wget -qO- https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-chrome-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$(curl -sS https://chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy app files
COPY . .

# Ensure Python can find the app
ENV PYTHONPATH=/app

# Expose the FastAPI port
EXPOSE 8000

# Run FastAPI server with correct module path
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
