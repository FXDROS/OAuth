import models
import string
import random
import secrets
import bcrypt
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, status, HTTPException, Form, Depends, Request
from pydantic import BaseModel, Field
from database import SessionLocal

app = FastAPI()
db = SessionLocal()

class Mahasiswa(BaseModel):
    username: str
    full_name: str
    npm: str
    password: str

    class Config:
        orm_mode=True

class LoginMahasiswa(BaseModel):
    username: str
    password: str
    grant_type: str
    client_id: str
    client_secret: str

    class Config:
        orm_mode=True

def generateRandomString(length):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for x in range(length))

async def verifyToken(req: Request):
    token = req.headers["Authorization"]
    token = token[7:]

    mahasiswa_db = db.query(models.Mahasiswa).filter(models.Mahasiswa.access_token == token).first()

    if mahasiswa_db is None:
        raise HTTPException(status_code=401, detail="Unauthorized user")

    nowTime = datetime.now()
    created_at = mahasiswa_db.token_created_at

    if (nowTime > created_at + timedelta(days = 3)):
        mahasiswa_db.access_token = None
        mahasiswa_db.refresh_token = None
        mahasiswa_db.token_created_at = None
        db.commit()

        raise HTTPException(status_code=401, detail="Unauthorized user: Token has expired")

    if (nowTime > created_at + timedelta(seconds = 300)):
        mahasiswa_db.access_token = None
        db.commit()

        raise HTTPException(status_code=401, detail="Unauthorized user: Token has expired")

    return mahasiswa_db

@app.post('/oauth/register', status_code=status.HTTP_201_CREATED)
def register(mahasiswa: Mahasiswa):
    mahasiswa_npm_check = db.query(models.Mahasiswa).filter(models.Mahasiswa.npm == mahasiswa.npm).first()
    mahasiswa_username_check = db.query(models.Mahasiswa).filter(models.Mahasiswa.username == mahasiswa.username).first()
    if (mahasiswa_npm_check or mahasiswa_username_check)is not None:
        raise HTTPException(status_code=400, detail="User already exist")

    hashed_password = bcrypt.hashpw(mahasiswa.password.encode('utf-8'), bcrypt.gensalt())
    hashed_password = hashed_password.decode('utf-8')
    client_secret = generateRandomString(40)

    new_mahasiswa = models.Mahasiswa(
        username=mahasiswa.username,
        npm=mahasiswa.npm,
        full_name=mahasiswa.full_name,
        password=hashed_password,
        client_secret=client_secret,
    )

    db.add(new_mahasiswa)
    db.commit()

    return {
        "username" : mahasiswa.username,
        "full_name" : mahasiswa.full_name,
        "npm" : mahasiswa.npm,
    }

@app.post('/oauth/token', status_code=status.HTTP_200_OK)
async def login(username: str = Form(...),
        password: str = Form(...),
        grant_type: str = Form(...),
        client_id: str = Form(...),
        client_secret: str = Form(...)
):
    mahasiswa_db = db.query(models.Mahasiswa).filter(models.Mahasiswa.username == username).first()
    if mahasiswa_db is None:
        raise HTTPException(status_code=401, detail="Invalid credential(s)")

    check_pswd = bcrypt.checkpw(password.encode('utf-8'), mahasiswa_db.password.encode('utf-8'))
    check_secret = (mahasiswa_db.client_secret == client_secret)
    check_id = (mahasiswa_db.client_id == int(client_id))

    print(mahasiswa_db.client_secret == client_secret)

    if (check_pswd and check_secret and check_id) is False:
        raise HTTPException(status_code=401, detail="Invalid credential(s)")

    access_token = generateRandomString(40)
    refresh_token = generateRandomString(40)
    token_created_at = datetime.now()

    mahasiswa_db.access_token = access_token
    mahasiswa_db.refresh_token = refresh_token
    mahasiswa_db.token_created_at = token_created_at

    db.commit()

    return {
        "access_token" : access_token,
        "expires_in" : 300,
        "token_type" : "bearer",
        "scope" : '',
        "refresh_token" : refresh_token
    }

@app.post('/oauth/resource')
def getResource(authorizeUser: Mahasiswa = Depends(verifyToken)):
    if authorizeUser:
        expires_in = timedelta(seconds = 300) - (datetime.now() - authorizeUser.token_created_at)

        return {
            "client_id" : str(authorizeUser.client_id),
            "username" : authorizeUser.username,
            "npm" : authorizeUser.npm,
            "full_name" : authorizeUser.full_name,
            "access_token" : authorizeUser.access_token,
            "expires_in" : expires_in,
            "refresh_token" : authorizeUser.refresh_token
        }

@app.get('/')
def index():
    return { "Welcome To Dion's OAuth" }