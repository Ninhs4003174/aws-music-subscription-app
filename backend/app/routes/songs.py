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

    items = []

    try:
        if artist and year:
            query_params["IndexName"] = "artist-year-lsi"
            query_params["KeyConditionExpression"] = Key('artist').eq(artist) & Key('year').eq(year)
            response = table.query(**query_params)
            items = response.get('Items', [])
        elif artist:
            query_params["KeyConditionExpression"] = Key('artist').eq(artist)
            response = table.query(**query_params)
            items = response.get('Items', [])
        else:
            # Scan all items (fallback approach for flexible filtering)
            response = table.scan(**query_params)
            items = response.get('Items', [])
    except ClientError:
        items = []

    # Prefix/partial matching with case-insensitive filtering
    def match(song):
        # Helper: case-insensitive prefix match
        def prefix_match(field_value, search_term):
            if not search_term:
                return True
            if not field_value:
                return False
            return str(field_value).lower().startswith(str(search_term).lower())
        
        return (
            (not title or prefix_match(song.get('title', ''), title)) and
            (not artist or prefix_match(song.get('artist', ''), artist)) and
            (not year or str(song.get('year', '')) == str(year)) and
            (not album or prefix_match(song.get('album', ''), album))
        )

    filtered = list(filter(match, items))[:limit]

    if not filtered:
        return []

    # Pre-signed URLs
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


@router.options("/music/query")
def options_music_query():
    return {}

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
