from fastapi import APIRouter, HTTPException
from app.models.schemas import RegisterRequest, LoginRequest
import boto3
import os

router = APIRouter()
AWS_REGION = os.getenv('AWS_REGION') or os.getenv('AWS_DEFAULT_REGION') or 'us-east-1'
table = boto3.resource('dynamodb', region_name=AWS_REGION).Table('login')

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

    # Support both field names (username or user_name) for AWS compatibility
    item = res['Item']
    username = item.get('username') or item.get('user_name') or req.email

    return {
    "email": req.email,
    "username": username
    }