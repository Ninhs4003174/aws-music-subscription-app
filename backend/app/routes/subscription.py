from fastapi import APIRouter
from app.models.schemas import SubscriptionRequest
import boto3
from boto3.dynamodb.conditions import Key

router = APIRouter()

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('subscriptions')

@router.post("/subscribe")
def subscribe(req: SubscriptionRequest):
    table.put_item(Item={
        'user_email': req.user_email,
        'song_id': req.song_id
    })
    return {"message": "subscribed"}


@router.delete("/subscribe")
def unsubscribe(req: SubscriptionRequest):
    table.delete_item(
        Key={
            'user_email': req.user_email,
            'song_id': req.song_id
        }
    )
    return {"message": "removed"}


@router.get("/subscriptions/{user_email}")
def get_subscriptions(user_email: str):
    response = table.query(
        KeyConditionExpression=Key('user_email').eq(user_email)
    )
    return response.get('Items', [])