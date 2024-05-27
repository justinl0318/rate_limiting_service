# base image
FROM python:3.8-slim

# set working direcotry
WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "rate_limiter_without_redis.py"]
