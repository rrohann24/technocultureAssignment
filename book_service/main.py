from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
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


books_db = {}

# Dapr sidecar address
dapr_address = "http://localhost:3500/v1.0/invoke"

class Book(BaseModel):
    title: str
    author: str


@app.post("/books", response_model=Book)
def create_book(book: Book):
    # Generate a unique ID for the book
    book_id = str(uuid.uuid4())
    book_dict = book.dict()
    book_dict["id"] = book_id

    # Store the book in the in-memory database
    books_db[book_id] = book_dict

    # Publish a book created event using Dapr Pub/Sub
    event_data = {"book_id": book_id, "title": book.title, "author": book.author}
    requests.post(f"{dapr_address}/book-service/publish/book-created", json=event_data)

    return book_dict


@app.get("/books", response_model=List[Book])
def get_all_books():
    return list(books_db.values())


@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: str):
    if book_id in books_db:
        return books_db[book_id]
    else:
        raise HTTPException(status_code=404, detail="Book not found")
