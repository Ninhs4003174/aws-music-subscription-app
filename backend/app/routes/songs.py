from fastapi import APIRouter
from app.models.schemas import SongQuery
import boto3
from boto3.dynamodb.conditions import Key
from app.services.s3 import generate_presigned_url

router = APIRouter()

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('music')


@router.post("/songs")
def query_songs(req: SongQuery):

    # Step 1: Use Query if artist provided
    if req.artist:
        response = table.query(
            KeyConditionExpression=Key('artist').eq(req.artist)
        )
        items = response['Items']
    else:
        response = table.scan()
        items = response['Items']

    # Step 2: Apply AND filtering
    def match(song):
        return (
            (not req.year or song['year'] == req.year) and
            (not req.album or song['album'] == req.album) and
            (not req.title or song['title'] == req.title)
        )

    filtered = list(filter(match, items))

    if not filtered:
        return {"message": "No result is retrieved. Please query again"}

    # Step 3: Replace image_url with pre-signed URL
    for song in filtered:
        if "image_url" in song:
            song["image_url"] = generate_presigned_url(song["image_url"])

    return filtered