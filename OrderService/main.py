# OrderService/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json

app = FastAPI()

class Order(BaseModel):
    user_id: int
    book_id: int
    quantity: int

orders_db = {}
order_id_counter = 1

@app.post("/orders", response_model=Order)
def create_order(order: Order):
    global order_id_counter
    order_id = order_id_counter
    order_id_counter += 1

    # Validate book existence using Dapr invoke
    book_response = invoke_book_service("GET", f"/books/{order.book_id}")
    if book_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Invalid book ID")

    orders_db[order_id] = order
    notify_order_creation(order_id)
    return {**order.dict(), "order_id": order_id}

def notify_order_creation(order_id: int):
    # Using Dapr PubSub to notify the NotificationService about order creation
    payload = json.dumps({"order_id": order_id})
    requests.post("http://localhost:3500/v1.0/publish/pubsub", data=payload, headers={"Content-Type": "application/json"})

def invoke_book_service(method: str, path: str):
    # Using dapr invoke to communicate with BookService
    url = "http://localhost:3500/v1.0/invoke/book-service/method" + path
    return requests.request(method, url)
