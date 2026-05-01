from fastapi import APIRouter
import boto3
from boto3.dynamodb.conditions import Key
from app.services.s3 import generate_presigned_url

router = APIRouter()

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('music')


@router.get("/songs")
def query_songs(
    artist: str = None,
    year: str = None,
    album: str = None,
    title: str = None,
    limit: int = 50,
    last_evaluated_key: str = None
):

    # ✅ Requirement: at least one field must be provided
    if not any([artist, year, album, title]):
        return {"message": "At least one field must be provided"}

    # Pagination setup
    exclusive_start_key = None
    if last_evaluated_key:
        import json
        exclusive_start_key = json.loads(last_evaluated_key)

    query_params = {
        "Limit": limit
    }

    if exclusive_start_key:
        query_params["ExclusiveStartKey"] = exclusive_start_key

    # ✅ Use indexes properly
    if artist and year:
        response = table.query(
            IndexName='artist-year-index',
            KeyConditionExpression=Key('artist').eq(artist) & Key('year').eq(year),
            **query_params
        )
        items = response['Items']

    elif artist and album:
        response = table.query(
            IndexName='artist-album-index',
            KeyConditionExpression=Key('artist').eq(artist) & Key('album').eq(album),
            **query_params
        )
        items = response['Items']

    elif artist:
        response = table.query(
            KeyConditionExpression=Key('artist').eq(artist),
            **query_params
        )
        items = response['Items']

    else:
        response = table.scan(**query_params)
        items = response['Items']

    # ✅ FULL AND filtering
    def match(song):
        return (
            (not title or song['title'] == title) and
            (not year or song['year'] == year) and
            (not album or song['album'] == album)
        )

    filtered = list(filter(match, items))

    if not filtered:
        return {"message": "No result is retrieved. Please query again"}

    # ✅ Pre-signed URLs
    for song in filtered:
        if "image_url" in song:
            song["image_url"] = generate_presigned_url(song["image_url"])

    result = {
        "items": filtered
    }

    if "LastEvaluatedKey" in response:
        import json
        result["last_evaluated_key"] = json.dumps(response["LastEvaluatedKey"])

    return result
