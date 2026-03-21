from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()
items = []

@app.post("/api/graphql")
async def graphql():
    if not items:
        items.append({
            "id": 1,
            "name": "Initial",
            "sku": "INIT"
        })

    return JSONResponse({
        "data": {
            "items": items
        }
    })