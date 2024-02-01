from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Dapr sidecar address
dapr_address = "http://localhost:3500/v1.0/invoke"

class Notification(BaseModel):
    user_id: str
    message: str


@app.post("/notifications", response_model=Notification)
def send_notification(notification: Notification):
    # In a real-world scenario, you might use a notification service to send messages.
    # For simplicity, we'll just print the notification.

    # Subscribe to the book-created event using Dapr Pub/Sub
    event_data = {"user_id": notification.user_id, "message": notification.message}
    requests.post(f"{dapr_address}/notification-service/publish/order-update", json=event_data)

    print(f"Notification to {notification.user_id}: {notification.message}")
    return notification
