FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8000

ENV PORT=10000

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]

