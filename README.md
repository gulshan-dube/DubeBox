# 🚀 DubeBox
**Flask + Redis microservice with Docker Compose and persistent storage**

DubeBox is a hands‑on, portfolio‑ready microservice: a Python Flask API talking to a Redis backend, orchestrated with Docker Compose.  
It demonstrates containerization, private inter‑container networking, and persistence via Docker volumes.  
It maps cleanly to AWS ECS (Fargate) for cloud deployment.


---


## 🧠 Real‑world analogy

## It's like running a little café:

- Flask is the chef who cooks every order on the spot.
- Redis is the fridge that holds quick‑grab ingredients the chef needs constantly.
- Docker is the food truck that carries the chef and the fridge together wherever you go — they’re always side‑by‑side, ready to work.
- The private kitchen (Docker network) is the truck’s inside workspace, where only the chef and fridge can talk — no strangers allowed.
- A named volume is the hidden pantry inside the truck that keeps its stock even after you shut the truck down for the night, so you don’t lose everything when you reopen in the morning.

---

## 🎯 Project goals
- **Containerize:** Build a lightweight Flask API image  
- **Compose:** Run Flask + Redis together with service discovery by name  
- **Network:** Keep Redis private; expose only Flask on host port 5000  
- **Persist:** Add a named volume so Redis data survives container restarts  
- **Explain:** Map the local pattern to AWS ECS for interviews  

---

## 🛠 Tech stack

| Component | Purpose |
|---|---|
| Flask | Web API layer on port 5000 |
| Redis | In‑memory key/value store on port 6379 |
| Docker | Containerization of the app |
| Docker Compose | Multi‑container orchestration |
| Docker volumes | Persistent Redis data across restarts |
| GitHub | Code and documentation hosting |

---

## 📁 Folder structure
```
DubeBox/
├── app.py                # Flask API
├── requirements.txt      # Python dependencies
├── Dockerfile            # Flask image build
├── docker-compose.yml    # Orchestrates Flask + Redis + volume
└── README.md             # This document
```

---

## ⚙️ How it works
- **Two containers:** Flask (web) and Redis (redis) run in one Compose project  
- **Private network:** Compose creates a network; Flask reaches Redis at hostname `redis`  
- **Single public port:** Only Flask maps host port 5000 → container 5000  
- **Persistence:** A named volume `redis_data` mounts at `/data`, so Redis retains keys after restarts  

---

## 🧾 Quick start
```bash
# Clone and enter
git clone https://github.com/<your-username>/DubeBox.git
cd DubeBox

# Bring everything up (build on first run)
docker-compose up --build
```

**Test in your browser or Postman:**
- http://localhost:5000/
- http://localhost:5000/set/name/G
- http://localhost:5000/get/name

**Shut down and clean up containers (keep the volume/data):**
```bash
CTRL+C
docker-compose down
```

---

## 🧪 Persistence test (named volume)
```bash
# With services running:
curl http://localhost:5000/set/test/123
curl http://localhost:5000/get/test   # returns 123

# Restart services
docker-compose down
docker-compose up

# Data should persist
curl http://localhost:5000/get/test   # still returns 123
```

### 📂 What is a named volume in this project?

A **named volume** in Docker is storage that lives **outside** the container’s filesystem, with a specific label so Docker can re‑use it even if the container is removed.  

In **DubeBox**, the line:
```yaml
volumes:
  - redis_data:/data
```
inside the `redis` service, and:
```yaml
volumes:
  redis_data:
```
at the bottom of `docker-compose.yml` creates a volume named **`redis_data`**.  

- `/data` is Redis’s default path for storing its database.  
- `redis_data` is managed by Docker and survives container restarts.  
- This means keys you store in Redis are still there after stopping/starting containers.

**See it yourself:**
```bash
# List all named volumes
docker volume ls

# Inspect the redis_data volume
docker volume inspect redis_data
```

---

## 📦 Source files

### **app.py**
```python
from flask import Flask, jsonify
import redis
import os

app = Flask(__name__)

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

@app.route("/")
def home():
    return jsonify({"message": "Welcome to DubeBox 🚀", "status": "running"})

@app.route("/set/<key>/<value>")
def set_value(key, value):
    r.set(key, value)
    return jsonify({"message": f"Stored {key} → {value} in Redis"})

@app.route("/get/<key>")
def get_value(key):
    value = r.get(key)
    return jsonify({"key": key, "value": value})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
```

### **requirements.txt**
```
flask==2.3.2
redis==5.0.1
```

### **Dockerfile**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py"]
```

### **docker-compose.yml**
```yaml
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
    volumes:
      - redis_data:/data

volumes:
  redis_data:
```

---

## 🧰 Useful commands
```bash
# Build + run
docker-compose up --build

# View logs
docker-compose logs web

# Stop + remove containers (keep volume)
docker-compose down

# Full reset (remove containers + volumes)
docker-compose down -v
```

---

## 🐞 Common errors and fixes

**Port 5000 already in use**  
Cause: AirPlay Receiver binding port 5000  
Fix: Disable AirPlay or change mapping:
```bash
docker-compose up --build -p 5050:5000
```

**Redis connection errors**  
Cause: Wrong host or Redis not ready  
Fix: Use:
```env
REDIS_HOST=redis
REDIS_PORT=6379
```

**YAML validation errors**  
Cause: Bad indentation or missing `-`  
Fix: Use exact format shown in `docker-compose.yml` above

**Data lost after restart**  
Cause: No volume for Redis  
Fix: Add named volume as above

**`zsh: command not found: code`**  
Cause: VS Code CLI not installed  
Fix: Install via Cmd+Shift+P → Shell Command: Install 'code' command in PATH

**Git push asks for username/password**  
Cause: HTTPS remote needs PAT  
Fix: Create token with `repo` scope or switch to SSH

**Terminal stuck at `quote>` prompt**  
Cause: Multi‑line paste triggered interactive mode  
Fix: Ctrl+C, paste commands line‑by‑line

---

## 🖥️ AWS mapping
| Local element | AWS equivalent |
|---|---|
| 2 services in Compose | 2 container defs in ECS task |
| Docker network | ECS `awsvpc` networking |
| Env vars in Compose | ECS env vars / Secrets Manager |
| Flask port 5000 | ALB/NLB listener |
| Redis private port 6379 | Internal only |
| Named volume for Redis | EBS/EFS persistence |

---

## 🧹 Cleanup
```bash
# Containers only
docker-compose down

# Containers + volumes
docker-compose down -v

# Prune unused images
docker system prune -f
```

---
