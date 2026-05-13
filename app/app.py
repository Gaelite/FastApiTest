from fastapi import FastAPI, status, HTTPException, Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from schemas import UserOut, UserAuth, TokenSchema, infoInput, infoOutput
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

@app.post('/upload-data', response_model=infoOutput)
async def upload_data(data: infoInput, user: Annotated[dict, Depends(get_current_user)], db: Annotated[sqlite3.Connection, Depends(get_db)]):
    cur = db.cursor()

    cur.execute(
        "INSERT INTO info (userId, data) VALUES (?, ?)",
        (user["id"], data.info)
    )

    db.commit()

    return {
        "info": data.info,
        "user": user["username"]
    }

@app.get('/get-data')
async def get_data(data: infoInput, user: Annotated[dict, Depends(get_current_user)], db: Annotated[sqlite3.Connection, Depends(get_db)]):
    cur = db.cursor()

    cur.execute(
        "SELECT data from info WHERE userid = ?", (user["id"],)
    )

    info = cur.fetchall()

    if not info:
        raise HTTPException(
            status_code=400,
            detail="No data"
        )

    return {
        "info": info
    }

@app.delete('/delete-all-data')
async def delete_all_data( user: Annotated[dict, Depends(get_current_user)], db: Annotated[sqlite3.Connection, Depends(get_db)]):
    cur = db.cursor()

    cur.execute(
        "DELETE FROM info WHERE userId = ?",
        (user["id"],)
    )

    db.commit()

    return {"msg": "All data deleted"}

@app.get("/")
def read_root():
    return {"Hello": "World"}