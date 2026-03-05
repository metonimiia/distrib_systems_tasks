import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../app')))
from main import app

client = TestClient(app)

def test_update_success():
    create_response = client.post("/orders", json={
        "name": "Test Object",
        "priority": 5 
    })
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]
    
    update_response = client.put(f"/orders/{item_id}", json={
        "name": "Updated Object",
        "priority": 10 
    })
    assert update_response.status_code == 200
    updated_data = update_response.json()
    assert updated_data["name"] == "Updated Object"
    assert updated_data["priority"] == 10 
    assert updated_data["id"] == item_id
    get_response = client.get(f"/orders/{item_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Updated Object"

def test_delete_not_found():
    response = client.delete("/orders/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"
