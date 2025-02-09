# Content Moderation API

This project provides an API that checks if text or images contain harmful or inappropriate content. It uses **OpenAI’s moderation tools** to perform this check. The system is built using **FastAPI** for the API, **Celery** to process tasks in the background, **Redis** to cache results for speed, and **PostgreSQL** to save moderation results.

## Table of Contents

- [How to Set Up](#how-to-set-up)
- [API Endpoints](#api-endpoints)
- [How It Works](#how-it-works)
- [Performance Tips](#performance-tips)
- [Docker Setup](#docker-setup)
- [Load Testing](#load-testing)

---

## **How to Set Up**

### **What You Need**

Before you start, you need to have these tools installed:

1. **Docker**: This helps you run the app easily in containers.
2. **Docker Compose**: This lets you run multiple parts of the app together.
3. **Git**: To clone the project.

### **Steps to Set It Up**

#### **Clone the repository**

First, download the project by running this command:

```bash
git clone https://github.com/harichselvamc/assignment.git

cd assignment
```





### **Set up your environment variables**

Create a `.env` file in the project folder. This file will hold sensitive information (like database credentials and API keys).  
Here’s an example of what it should contain:

```env
DATABASE_URL=postgresql://user:password@db:5432/moderation_db
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
OPENAI_API_KEY=openai-api-key
```
# Run the App with Docker

You can easily start the app using Docker by running this command:

```bash
docker-compose up --build
```

This will start all the services (API, Redis, PostgreSQL, and Celery worker).

## Check the Logs (Optional)

To see what's happening with the API service, you can use:

```bash
docker-compose logs -f api
```

## Install Python Dependencies (Optional)

If you want to run the app without Docker, you can install the necessary libraries manually with:

```bash
pip install -r requirements.txt
```

## Run the FastAPI App (Optional)

If you're running it manually, use this command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

# API Endpoints

## 1. Health Check
**GET** `/api/v1/health`

**Description:** Check if the app is running.

**Response:**
```json
{
  "status": "OK"
}
```

## 2. Moderate Text
**POST** `/api/v1/moderate/text`

**Request Body:**
```json
{
  "text": "Some text to check for harmful content."
}
```

**Response:**
```json
{
  "id": "modr-970d409ef3bef3b70c73d8232df86e7d",
  "model": "omni-moderation-latest",
  "results": [
    {
      "flagged": true,
      "categories": {
        "sexual": false,
        "sexual/minors": false,
        "harassment": false,
        "harassment/threatening": false,
        "hate": false,
        "hate/threatening": false,
        "illicit": false,
        "illicit/violent": false,
        "self-harm": false,
        "self-harm/intent": false,
        "self-harm/instructions": false,
        "violence": true,
        "violence/graphic": false
      },
      "category_scores": {
        "sexual": 2.34135824776394e-7,
        "sexual/minors": 1.6346470245419304e-7,
        "harassment": 0.0011643905680426018,
        "harassment/threatening": 0.0022121340080906377,
        "hate": 3.1999824407395835e-7,
        "hate/threatening": 2.4923252458203563e-7,
        "illicit": 0.0005227032493135171,
        "illicit/violent": 3.682979260160596e-7,
        "self-harm": 0.0011175734280627694,
        "self-harm/intent": 0.0006264858507989037,
        "self-harm/instructions": 7.368592981140821e-8,
        "violence": 0.8599265510337075,
        "violence/graphic": 0.37701736389561064
      }
    }
  ]
}
```

## 3. Moderate Image
**POST** `/api/v1/moderate/image`

**Request Body:**
```json
{
  "image": "base64_encoded_image_string"
}
```

**Response:**
```json
{
  "id": "modr-970d409ef3bef3b70c73d8232df86e7d",
  "model": "omni-moderation-latest",
  "results": [
    {
      "flagged": true,
      "categories": {
        "sexual": false,
        "sexual/minors": false,
        "harassment": false,
        "harassment/threatening": false,
        "hate": false,
        "hate/threatening": false,
        "illicit": false,
        "illicit/violent": false,
        "self-harm": false,
        "self-harm/intent": false,
        "self-harm/instructions": false,
        "violence": true,
        "violence/graphic": false
      },
      "category_scores": {
        "sexual": 2.34135824776394e-7,
        "sexual/minors": 1.6346470245419304e-7,
        "harassment": 0.0011643905680426018,
        "harassment/threatening": 0.0022121340080906377,
        "hate": 3.1999824407395835e-7,
        "hate/threatening": 2.4923252458203563e-7,
        "illicit": 0.0005227032493135171,
        "illicit/violent": 3.682979260160596e-7,
        "self-harm": 0.0011175734280627694,
        "self-harm/intent": 0.0006264858507989037,
        "self-harm/instructions": 7.368592981140821e-8,
        "violence": 0.8599265510337075,
        "violence/graphic": 0.37701736389561064
      }
    }
  ]
}
```

# How It Works

Here’s a simple explanation of how everything works together:

1. The user sends a request to the API to moderate either a piece of text or an image.
2. The request is sent to Celery, which handles the task in the background so the app doesn’t get stuck waiting for results.
3. The request is sent to OpenAI's moderation model to check for harmful or inappropriate content.
4. The result is stored in Redis so if the same text or image is checked again, it can be quickly fetched.
5. The result is also saved in PostgreSQL so we have a permanent record of all moderation checks.

# Performance Tips

- **Background processing:** We use Celery to handle the heavy work in the background, so the main API remains responsive.
- **Caching:** Redis is used to cache results. This speeds things up when the same content is checked multiple times.
- **Persistent storage:** All moderation results are saved in PostgreSQL, so we can track everything over time and avoid data loss.

# Docker Setup

Docker makes it easy to run this app by packaging everything into containers. Here’s a breakdown of what each container does:

- **API:** The FastAPI service running on port 8000.
- **PostgreSQL:** The database running on port 5432.
- **Redis:** The cache and task broker running on port 6379.
- **Celery Worker:** The background task processor for moderation checks.

To start everything, just run:

```bash
docker-compose up --build
```

# Load Testing

Once the app is running, you might want to test how it performs under load.

Here’s a basic way to test using Artillery, a simple load testing tool:

### Install Artillery:

```bash
npm install -g artillery
```

### Create a test file (`test.yaml`):

```yaml
config:
  target: 'http://localhost:8000'
  phases:
    - duration: 60
      arrivalRate: 10

scenarios:
  - flow:
      - post:
          url: "/api/v1/moderate/text"
          json:
            text: "Text to moderate."
```

### Run the test:

```bash
artillery run test.yaml
```

This will simulate 10 requests per second for 1 minute and show you the results.

