FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py db.py models.py part2.py verify_seed.py demo_api.py start.py ./
COPY dashboard.html ./
COPY sql ./sql
CMD ["python", "start.py"]
