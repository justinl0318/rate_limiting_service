# base image
FROM python:3.8-slim

# set working directory
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "hello_world.py"]
