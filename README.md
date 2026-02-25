# AI-Powered Sentiment Analysis API

This project demonstrates a complete DevOps pipeline using Docker to **build**, **ship**, and **deploy** a simple AI‑powered Flask application. The API accepts text and returns a sentiment classification (POSITIVE, NEGATIVE, NEUTRAL) using a transformer model from Hugging Face.

---

## Table of Contents

- [Set up a virtual environment](#Set-up-a-environment)
- [Dockerize the Application](#dockerize-the-application)
- [CI/CD with GitHub Actions](#cicd-with-github-actions)

---

## Run Locally

Follow these steps to run the Flask API on your local machine.

### Prerequisites

- Python 3.8 or higher installed ([python.org](https://python.org))
- `pip` (usually comes with Python)
- (Optional) `git` to clone the repository

### Step 1: Set up a virtual environment

```bash
python -m venv venv
```

##### Activate it
```bash
Windows: venv\Scripts\activate

macOS/Linux: source venv/bin/activat
```
##### Install Dependencies
```bash
pip install -r requirements.txt
```

##### Run the Flask application
```bash
python app.py
```

_expected outcome:_
```yml
Running on http://127.0.0.1:5000
```

##### Test the API
```xml
curl -X POST http://127.0.0.1:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "It is an ordinary day."}'
```

```json
{
  "text": "It is an ordinary day."
}
```

### Step 2: Dockerize the Application
* Create Dockerfile
* Build the docker image
```bash
docker build -t sentiment-api:latest .
```
* Run the container locally
```bash
docker run -d -p 5000:5000 --name sentiment-api sentiment-api:latest
```

* Ship the Container
```bash
docker push yourusername/sentiment-api:latest
```

### Step 3: CI/CD with GitHub Actions
* Create .github/workflows/docker-ci.yml in your repository:

```yml
name: Build, Ship, Deploy

on:
  pull_request:
    branches: [ master ]   # triggers on PRs targeting master

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build-and-push:
    name: Build & Push Docker Image
    runs-on: ubuntu-latest
    # Optional: skip deployment for PRs if you only want to build/test
    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to Docker Hub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            yourusername/sentiment-api:latest
            yourusername/sentiment-api:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy:
    name: Deploy to Server
    needs: build-and-push
    runs-on: ubuntu-latest
    # Only deploy if it's a PR from the same repository (to avoid exposing secrets on forks)
    if: github.event.pull_request.head.repo.full_name == github.repository
    steps:
      - name: Deploy to server via SSH
        uses: appleboy/ssh-action@v1.2.5
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            set -e
            IMAGE="yourusername/sentiment-api"
            TAG="${{ github.sha }}"
            echo "🔄 Pulling image $IMAGE:$TAG ..."
            docker pull $IMAGE:$TAG
            echo "🛑 Stopping old container..."
            docker stop sentiment-api || true
            echo "🗑️ Removing old container..."
            docker rm sentiment-api || true
            echo "🚀 Starting new container..."
            docker run -d \
              --restart unless-stopped \
              -p 5000:5000 \
              --name sentiment-api \
              $IMAGE:$TAG
            echo "✅ Deployment completed successfully!"
```