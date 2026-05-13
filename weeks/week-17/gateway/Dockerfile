FROM python:3.11-slim
WORKDIR /app
COPY gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY proto /app/proto
RUN python -m grpc_tools.protoc -I/app/proto --python_out=/app --grpc_python_out=/app /app/proto/events.proto

COPY gateway/main.py /app/main.py
ENV EVENTS_SVC_HOST=events-svc-s12:8257
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
