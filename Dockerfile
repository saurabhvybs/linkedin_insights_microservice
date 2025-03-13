# Use the official Python image
FROM python:3.13

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Chrome & Chromedriver for Selenium
RUN apt-get update && apt-get install -y \
    wget unzip curl \
    && wget -qO- https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/goog
