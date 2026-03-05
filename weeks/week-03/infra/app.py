import os
from fastapi import FastAPI, HTTPException

app = FastAPI()
resource_path = os.getenv("RESOURCE_PATH", "/resource")
service_name = os.getenv("SERVICE_NAME", "mock-service")

@app.get("/{path:path}")
def handle(path: str):
    current_path = f"/{path}"
    if current_path != resource_path:
        raise HTTPException(status_code=404, detail="Not Found")
    return {
        "service": service_name,
        "path": current_path,
    }
