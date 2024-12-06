FROM python:3.10-slim

RUN pip install fastapi uvicorn asyncpg

WORKDIR /app

COPY main.py .
COPY ./db ./db

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]