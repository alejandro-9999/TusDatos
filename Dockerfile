FROM tiangolo/uvicorn-gunicorn:python3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN python3 ./API/load_dataset.py

COPY . /app