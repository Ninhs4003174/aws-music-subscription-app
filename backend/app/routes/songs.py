from fastapi import APIRouter
import boto3
import os
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError
from app.services.s3 import generate_presigned_url

router = APIRouter()

AWS_REGION = os.getenv('AWS_REGION') or os.getenv('AWS_DEFAULT_REGION') or 'us-east-1'
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
table = dynamodb.Table('music')


def _query_songs_core(
    artist: str = None,
    year: str = None,
    album: str = None,
    title: str = None,
    limit: int = 50,
    last_evaluated_key: str = None
):

    # ✅ Requirement: at least one field must be provided
    if not any([artist, year, album, title]):
        return []

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

    # Try query/index-first for speed, but fall back to scan if table schema differs.
    try:
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
    except ClientError as error:
        code = error.response.get('Error', {}).get('Code')
        if code != 'ValidationException':
            raise

        response = table.scan(**query_params)
        items = response.get('Items', [])

    # ✅ FULL AND filtering
    def match(song):
        return (
            (not title or song['title'] == title) and
            (not year or song['year'] == year) and
            (not album or song['album'] == album)
        )

    filtered = list(filter(match, items))

    if not filtered:
        return []

    # ✅ Pre-signed URLs
    for song in filtered:
        if "image_url" in song:
            song["image_url"] = generate_presigned_url(song["image_url"])

    return filtered


@router.get("/songs")
def query_songs(
    artist: str = None,
    year: str = None,
    album: str = None,
    title: str = None,
    limit: int = 50,
    last_evaluated_key: str = None
):
    items = _query_songs_core(artist, year, album, title, limit, last_evaluated_key)
    return {"items": items}


@router.get("/music/query")
def query_music_for_frontend(
    artist: str = None,
    year: str = None,
    album: str = None,
    title: str = None,
    limit: int = 50,
    last_evaluated_key: str = None
):
    # Frontend expects a raw array.
    return _query_songs_core(artist, year, album, title, limit, last_evaluated_key)
