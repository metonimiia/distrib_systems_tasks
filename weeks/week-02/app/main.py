from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List

app = FastAPI()

# Модель для создания (без id)
class OrderCreate(BaseModel):
    name: str
    priority: int 

# Модель для ответа (с id)
class Order(OrderCreate):
    id: int

db = []
counter = 1
 
@app.get("/orders", response_model=List[Order])
async def get_all():
    return db

@app.get("/orders/{item_id}", response_model=Order)
async def get_one(item_id: int):
    for item in db:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Order not found")

@app.post("/orders", response_model=Order, status_code=201)
async def create(item: OrderCreate):
    global counter
    new_item = {
        "id": counter,
        "name": item.name,
        "priority": item.priority
    }
    db.append(new_item)
    counter += 1
    return new_item

@app.put("/orders/{item_id}", response_model=Order)
async def update(item_id: int, item_update: OrderCreate):
    for i, item in enumerate(db):
        if item["id"] == item_id:
            db[i] = {
                "id": item_id,
                "name": item_update.name,
                "priority": item_update.priority
            }
            return db[i]
    raise HTTPException(status_code=404, detail="Order not found")

@app.delete("/orders/{item_id}", status_code=204)
async def delete(item_id: int):
    for i, item in enumerate(db):
        if item["id"] == item_id:
            db.pop(i)
            return
    raise HTTPException(status_code=404, detail="Order not found")