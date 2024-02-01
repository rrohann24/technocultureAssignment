from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


users_db = {}

class User(BaseModel):
    name: str
    email: str


@app.post("/users", response_model=User)
def create_user(user: User):
    # Generate a unique ID for the user
    user_id = str(uuid.uuid4())
    user_dict = user.dict()
    user_dict["id"] = user_id

    # Store the user in the in-memory database
    users_db[user_id] = user_dict

    return user_dict


@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: str):
    if user_id in users_db:
        return users_db[user_id]
    else:
        raise HTTPException(status_code=404, detail="User not found")
