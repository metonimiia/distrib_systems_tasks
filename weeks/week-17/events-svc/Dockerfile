FROM python:3.11-slim
WORKDIR /app
COPY events-svc/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY proto /app/proto
RUN python -m grpc_tools.protoc -I/app/proto --python_out=/app --grpc_python_out=/app /app/proto/events.proto

COPY events-svc/main.py /app/main.py
ENV PORT=8257
CMD ["python", "main.py"]
