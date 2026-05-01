from fastapi import APIRouter, HTTPException
from app.models.schemas import RegisterRequest, LoginRequest
import boto3

router = APIRouter()
table = boto3.resource('dynamodb').Table('login')

@router.post("/register")
def register(req: RegisterRequest):
    res = table.get_item(Key={'email': req.email})

    if 'Item' in res:
        raise HTTPException(400, "The email already exists")

    table.put_item(Item={
        'email': req.email,
        'username': req.username,
        'password': req.password
    })

    return {"message": "registered"}

@router.post("/login")
def login(req: LoginRequest):
    res = table.get_item(Key={'email': req.email})

    if 'Item' not in res or res['Item']['password'] != req.password:
        raise HTTPException(400, "email or password is invalid")

    return {
    "email": req.email,
    "username": res['Item']['username']
    }