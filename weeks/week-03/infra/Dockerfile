FROM python:3.12-slim
WORKDIR /app
RUN pip install fastapi uvicorn
COPY app.py /app/app.py
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080}"]
