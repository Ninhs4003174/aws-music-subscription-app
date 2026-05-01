from fastapi import APIRouter
from app.models.schemas import SubscriptionRequest
import boto3
from boto3.dynamodb.conditions import Key
from app.services.s3 import generate_presigned_url


router = APIRouter()

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('subscriptions')

@router.post("/subscribe")
def subscribe(req: SubscriptionRequest):
    table.put_item(Item={
        'user_email': req.user_email,
        'song_id': req.song_id,
        'title': req.title,
        'artist': req.artist,
        'album': req.album,
        'image_url': req.image_url
    })
    return {"message": "subscribed"}


@router.delete("/subscribe")
def unsubscribe(user_email: str, song_id: str):
    table.delete_item(
        Key={
            'user_email': user_email,
            'song_id': song_id
        }
    )
    return {
    "message": "removed",
    "song_id": song_id
    }


@router.get("/subscriptions/{user_email}")
def get_subscriptions(user_email: str):
    response = table.query(
        KeyConditionExpression=Key('user_email').eq(user_email)
    )

    items = response.get('Items', [])

    for item in items:
        if "image_url" in item:
            item["image_url"] = generate_presigned_url(item["image_url"])

    return items