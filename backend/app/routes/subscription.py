from fastapi import APIRouter, HTTPException
from app.models.schemas import SubscriptionRequest
import boto3
import os
from boto3.dynamodb.conditions import Key
from app.services.s3 import generate_presigned_url


router = APIRouter()

AWS_REGION = os.getenv('AWS_REGION') or os.getenv('AWS_DEFAULT_REGION') or 'us-east-1'
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table('subscriptions')


def _put_subscription(user_email: str, song_id: str, title: str, artist: str, album: str, image_url: str):
    table.put_item(Item={
        'user_email': user_email,
        'song_id': song_id,
        'title': title,
        'artist': artist,
        'album': album,
        'image_url': image_url
    })


def _list_subscriptions(user_email: str):
    response = table.query(
        KeyConditionExpression=Key('user_email').eq(user_email)
    )

    items = response.get('Items', [])

    for item in items:
        if "image_url" in item:
            item["image_url"] = generate_presigned_url(item["image_url"])

    return items

@router.post("/subscribe")
def subscribe(req: SubscriptionRequest):
    _put_subscription(req.user_email, req.song_id, req.title, req.artist, req.album, req.image_url)
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
    return _list_subscriptions(user_email)


@router.post("/subscriptions")
def subscribe_frontend(payload: dict):
    email = payload.get("email") or payload.get("user_email")
    song_id = payload.get("song_id")

    if not email or not song_id:
        raise HTTPException(status_code=400, detail="email and song_id are required")

    _put_subscription(
        user_email=email,
        song_id=song_id,
        title=str(payload.get("title") or ""),
        artist=str(payload.get("artist") or ""),
        album=str(payload.get("album") or ""),
        image_url=str(payload.get("image_url") or payload.get("s3_image_url") or "")
    )
    return {"message": "subscribed"}


@router.get("/subscriptions")
def get_subscriptions_frontend(email: str):
    return _list_subscriptions(email)


@router.delete("/subscriptions/{song_id}")
def unsubscribe_frontend(song_id: str, email: str):
    table.delete_item(
        Key={
            'user_email': email,
            'song_id': song_id
        }
    )
    return {"message": "removed", "song_id": song_id}