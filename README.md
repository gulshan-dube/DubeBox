DubeBox — Flask + Redis with Docker Compose
A minimal, interview‑ready microservice that runs a Flask API and a Redis backend as separate containers using Docker Compose. You’ll learn containerization, inter‑container networking, and how this maps to AWS ECS.

1) Overview
Goal: Build a portable microservice with a fast in‑memory store, orchestrated locally with Docker Compose, and explain how it maps to AWS.

Services:

Flask (web): HTTP API on port 5000

Redis (redis): In‑memory key/value store on port 6379

Why this matters:

Real‑world relevance: Caching and state storage with Redis are common in production systems and interviews.

Cloud translation: Mirrors an ECS task with two containers communicating over a private network.

2) Project structure
text
DubeBox/
├── app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── venv/               # local dev only (not used inside Docker image)
3) What each file does
app.py: Flask app with routes to set/get values in Redis.

requirements.txt: Python dependencies for the app and image build.

Dockerfile: Blueprint for building the Flask app image.

docker-compose.yml: Orchestrates Flask + Redis containers and networking.

venv/: Local virtual environment for bare‑metal testing (excluded from Git).

4) Setup and run
A) Prerequisites
Docker Desktop: Installed and running

Python 3 (optional): Only needed if you want to run Flask outside Docker

Postman or Browser: To hit endpoints

B) Local bare‑metal test (optional but recommended)
bash
# From project root
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
# Visit: http://localhost:5000
# Stop with CTRL+C
C) Build the Docker image
bash
docker build -t dubebox:latest .
D) Run single container (optional quick check)
bash
docker run --rm -p 5000:5000 dubebox:latest
# Visit: http://localhost:5000
# Stop with CTRL+C
E) Run multi‑container with Docker Compose
bash
docker-compose up --build
# Visit:
# 1) http://localhost:5000/
# 2) http://localhost:5000/set/name/G
# 3) http://localhost:5000/get/name
# Stop with CTRL+C, then:
docker-compose down
5) Code snippets
A) Flask app (app.py)
python
from flask import Flask, jsonify
import redis
import os

app = Flask(__name__)

# Read Redis connection from environment (provided by docker-compose)
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to DubeBox 🚀", "status": "running"})

@app.route('/set/<key>/<value>')
def set_value(key, value):
    r.set(key, value)
    return jsonify({"message": f"Stored {key} → {value} in Redis"})

@app.route('/get/<key>')
def get_value(key):
    value = r.get(key)
    return jsonify({"key": key, "value": value})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
B) Dependencies (requirements.txt)
text
flask==2.3.2
redis==5.0.1
C) Dockerfile
dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install deps first (leverages Docker layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Default start command
CMD ["python", "app.py"]
D) Docker Compose (docker-compose.yml)
yaml
version: '3.8'

services:
  web:
    build: .
    container_name: dubebox_web
    ports:
      - "5000:5000"
    depends_on:
      - redis
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379

  redis:
    image: redis:7-alpine
    container_name: dubebox_redis
    ports:
      - "6379:6379"
6) How it works (simple and technical)
Simple: You packed your app and its dependencies into a portable box (image), then ran two boxes (Flask + Redis) side‑by‑side with a wire between them (Docker network). Your browser talks to Flask; Flask talks to Redis.

Technical: Docker builds a layered filesystem from the Dockerfile. Compose creates a user‑defined bridge network; each service is addressable by its service name. Environment variables configure the Flask app’s Redis client. Port 5000 on the host maps to port 5000 in the web container; Redis uses 6379 internally and is reachable from the web container via hostname redis.

7) Architecture diagrams
A) ASCII (renders everywhere)
[ Browser / Postman ]  -->  localhost:5000
          │
          ▼
┌────────────────────────────┐
│ Flask App (Container: web) │
│ - Runs app.py               │
│ - Port 5000 exposed         │
└───────────────┬────────────┘
                │  (Docker internal network)
                ▼
┌────────────────────────────┐
│ Redis (Container: redis)   │
│ - Port 6379 internal        │
│ - In-memory key/value store │
└────────────────────────────┘
B) Mermaid (renders on GitHub)
mermaid
flowchart LR
  A[Browser / Postman] -- HTTP :5000 --> B(Flask App - web container)
  subgraph Docker Network
    B -- Redis protocol :6379 --> C[Redis - redis container]
  end
8) AWS mapping (interview‑ready)
Compose services → ECS Task Definition: Two container definitions (Flask and Redis) in a single task (awsvpc network mode).

Docker network → VPC networking: Containers share the task’s ENI; talk privately over the VPC. Service discovery by container name maps to ECS internal DNS.

Environment variables → ECS Task env/Secrets Manager: Same pattern for config; secrets would move to AWS Secrets Manager/SSM Parameter Store.

Host port 5000 → Load Balancer target: In ECS, expose Flask via an ALB/NLB; Redis remains internal (no public access).

Use this line in interviews: “Locally I ran Flask and Redis as two containers on one network via Docker Compose. In AWS, the same maps to an ECS task with two containers using awsvpc mode, with the app exposed through an ALB and Redis kept private within the VPC.”

9) Troubleshooting
Port 5000 already in use:

Cause: macOS AirPlay Receiver often binds 5000.

Fix: System Settings → General → AirDrop & Handoff → disable AirPlay Receiver, or run with -p 5050:5000 and visit http://localhost:5050.

Container exits immediately:

Cause: App crashed (missing deps) or main process ended.

Fix: Ensure redis is in requirements.txt; rebuild with docker-compose up --build; check docker-compose logs web.

Redis connection errors:

Cause: Wrong host/port or Redis not ready.

Fix: Use REDIS_HOST=redis; keep depends_on; try again after both containers show “ready” logs.

10) GitHub: create repo and push
A) .gitignore (add before first commit)
gitignore
# Python
__pycache__/
*.pyc

# Env
venv/
.env

# macOS
.DS_Store

# Docker
*.log
B) Initialize and push
bash
# From project root
git init
git add .
git commit -m "Init DubeBox: Flask + Redis via Docker Compose"
git branch -M main

# Create a new empty repo on GitHub named "DubeBox" (via web UI), then:
# SSH (recommended if your keys are set up)
git remote add origin git@github.com:<your-username>/DubeBox.git
# or HTTPS
# git remote add origin https://github.com/<your-username>/DubeBox.git

git push -u origin main
If you accidentally committed venv before adding .gitignore: git rm -r --cached venv && git add . && git commit -m "Remove venv from repo" && git push

11) Why we tested before Docker (quick)
Confidence: If it works bare‑metal but fails in Docker, you know the issue is container config, not code.

Speed: Fewer variables when debugging.

Parity: Easy to compare behavior inside vs. outside the container.

12) Next steps
Enhance endpoints: Add TTL, lists/hashes, error handling, and simple tests.

Docs: Add screenshots (browser results, logs); keep README concise and visual.

Cloud: Package for ECS (task definition + ALB), or show a Terraform plan for local → cloud parity.