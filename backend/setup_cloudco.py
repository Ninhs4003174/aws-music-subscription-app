import boto3
import json
import os
import re
import requests
from urllib.parse import urlparse
from botocore.exceptions import ClientError

REGION = "us-east-1"
BUCKET_NAME = "aws-music-app"

dynamodb = boto3.resource("dynamodb", region_name=REGION)
s3 = boto3.client("s3", region_name=REGION)


def get_songs():
    with open("2026a2_songs.json", "r") as f:
        data = json.load(f)

    if isinstance(data, dict):
        songs = data.get("songs") or data.get("Items") or data.get("music")
    else:
        songs = data

    if not isinstance(songs, list):
        raise ValueError("Could not find a list of songs in JSON file")

    return songs


def table_exists(table_name):
    try:
        dynamodb.Table(table_name).load()
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            return False
        raise


def create_login_table():
    if table_exists("login"):
        print("login table already exists")
        return

    table = dynamodb.create_table(
        TableName="login",
        KeySchema=[
            {"AttributeName": "email", "KeyType": "HASH"}
        ],
        AttributeDefinitions=[
            {"AttributeName": "email", "AttributeType": "S"}
        ],
        BillingMode="PAY_PER_REQUEST"
    )

    table.wait_until_exists()
    print("login table created")


def populate_login_table():
    table = dynamodb.Table("login")

    users = [
        {
            "email": "s1234560@student.rmit.edu.au",
            "user_name": "testuser0",
            "password": "012345"
        },
        {
            "email": "s1234561@student.rmit.edu.au",
            "user_name": "testuser1",
            "password": "112345"
        },
        {
            "email": "s1234562@student.rmit.edu.au",
            "user_name": "testuser2",
            "password": "212345"
        },
        {
            "email": "s1234563@student.rmit.edu.au",
            "user_name": "testuser3",
            "password": "312345"
        },
        {
            "email": "s1234564@student.rmit.edu.au",
            "user_name": "testuser4",
            "password": "412345"
        },
        {
            "email": "s1234565@student.rmit.edu.au",
            "user_name": "testuser5",
            "password": "512345"
        },
        {
            "email": "s1234566@student.rmit.edu.au",
            "user_name": "testuser6",
            "password": "612345"
        },
        {
            "email": "s1234567@student.rmit.edu.au",
            "user_name": "testuser7",
            "password": "712345"
        },
        {
            "email": "s1234568@student.rmit.edu.au",
            "user_name": "testuser8",
            "password": "812345"
        },
        {
            "email": "s1234569@student.rmit.edu.au",
            "user_name": "testuser9",
            "password": "912345"
        }
    ]

    for user in users:
        table.put_item(Item=user)

    print("login table populated")


def create_music_table():
    if table_exists("music"):
        print("music table already exists")
        return

    table = dynamodb.create_table(
        TableName="music",
        KeySchema=[
            {"AttributeName": "title", "KeyType": "HASH"},
            {"AttributeName": "artist", "KeyType": "RANGE"}
        ],
        AttributeDefinitions=[
            {"AttributeName": "title", "AttributeType": "S"},
            {"AttributeName": "artist", "AttributeType": "S"}
        ],
        BillingMode="PAY_PER_REQUEST"
    )

    table.wait_until_exists()
    print("music table created")


def load_music_data():
    table = dynamodb.Table("music")
    songs = get_songs()

    for song in songs:
        table.put_item(
            Item={
                "title": str(song.get("title", "")),
                "artist": str(song.get("artist", "")),
                "year": str(song.get("year", "")),
                "album": str(song.get("album", "")),
                "image_url": str(song.get("image_url") or song.get("img_url") or "")
            }
        )

    print("music data loaded")


def create_bucket():
    try:
        s3.head_bucket(Bucket=BUCKET_NAME)
        print("S3 bucket already exists")
        return
    except ClientError:
        pass

    if REGION == "us-east-1":
        s3.create_bucket(Bucket=BUCKET_NAME)
    else:
        s3.create_bucket(
            Bucket=BUCKET_NAME,
            CreateBucketConfiguration={"LocationConstraint": REGION}
        )

    print("S3 bucket created")


def safe_filename(text):
    return re.sub(r"[^a-zA-Z0-9._-]", "_", text)


def upload_artist_images():
    songs = get_songs()
    os.makedirs("artist_images", exist_ok=True)

    for song in songs:
        image_url = song.get("image_url") or song.get("img_url")

        if not image_url:
            print(f"Skipping {song.get('artist', 'unknown')} - no image URL")
            continue

        artist = safe_filename(str(song.get("artist", "unknown_artist")))
        title = safe_filename(str(song.get("title", "unknown_title")))

        parsed_url = urlparse(image_url)
        extension = os.path.splitext(parsed_url.path)[1]

        if not extension:
            extension = ".jpg"

        file_name = f"{artist}_{title}{extension}"
        local_path = os.path.join("artist_images", file_name)

        try:
            response = requests.get(image_url, timeout=10)

            if response.status_code == 200:
                with open(local_path, "wb") as f:
                    f.write(response.content)

                s3.upload_file(local_path, BUCKET_NAME, file_name)
                print(f"Uploaded {file_name}")
            else:
                print(f"Failed to download {image_url}")

        except Exception as e:
            print(f"Error downloading image for {artist}: {e}")


if __name__ == "__main__":
    create_login_table()
    populate_login_table()

    create_music_table()
    load_music_data()

    create_bucket()
    upload_artist_images()

    print("Setup complete")