from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Модель для создания (без id)
class LikeCreate(BaseModel):
    name: str
    target: str

# Модель для ответа (с id)
class Like(LikeCreate):
    id: int

db = []
counter = 1

@app.get("/likes", response_model=List[Like])
async def get_all():
    return db

@app.get("/likes/{item_id}", response_model=Like)
async def get_one(item_id: int):
    for item in db:
        if item["id"] == item_id:
            return item
    raise HTTPException(404, "Not found")

@app.post("/likes", response_model=Like, status_code=201)
async def create(item: LikeCreate):
    global counter
    new_item = {
        "id": counter,
        "name": item.name,
        "target": item.target
    }
    db.append(new_item)
    counter += 1
    return new_item