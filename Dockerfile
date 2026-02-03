FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8000

# Use shell form to expand $PORT environment variable
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
