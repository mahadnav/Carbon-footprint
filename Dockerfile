# Use a standard Python base image
FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD streamlit run app.py --server.port=$PORT --server.enableCORS=false --server.headless=true
