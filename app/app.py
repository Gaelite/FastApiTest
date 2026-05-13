from fastapi import FastAPI, status, HTTPException, Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from schemas import UserOut, UserAuth, TokenSchema
from deps import get_current_user, get_db
import sqlite3
from utils import (
    get_hashed_password,
    create_access_token,
    create_refresh_token,
    verify_password
)
from uuid import uuid4

app = FastAPI()

@app.post('/signup', response_model=UserOut)
async def create_user(data: UserAuth, db: Annotated[sqlite3.Connection, Depends(get_db)]
):
    cur = db.cursor()

    # verify if user existt
    cur.execute("SELECT * FROM users WHERE username = ?", (data.username,))
    user = cur.fetchone()

    if user:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )

    # insert usar
    cur.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        (data.username, get_hashed_password(data.password,))
    )
    db.commit()

    return {
        "username": data.username
        }

@app.post('/login', response_model=TokenSchema)
async def login( data: UserAuth, db: Annotated[sqlite3.Connection, Depends(get_db)]):
    cur = db.cursor()

    cur.execute("SELECT * FROM users WHERE username = ?", (data.username,))
    user = cur.fetchone()

    if not user or not verify_password(data.password, user["password"]):
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password"
        )

    return {
        "access_token": create_access_token(user["username"]),
        "refresh_token": create_refresh_token(user["username"]),
    }

@app.get("/health-secure")
async def health_secure(user = Depends(get_current_user)):
    return {
        "status": "ok",
        "user": user["username"]
    }

@app.get("/")
def read_root():
    return {"Hello": "World"}