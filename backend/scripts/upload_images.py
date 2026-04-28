import json
import boto3
import requests
from urllib.parse import urlparse

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

BUCKET_NAME = "your-bucket-name"
TABLE_NAME = "music"

table = dynamodb.Table(TABLE_NAME)

def get_filename_from_url(url):
    return urlparse(url).path.split("/")[-1]

def upload_image_to_s3(image_url):
    filename = get_filename_from_url(image_url)

    response = requests.get(image_url)
    if response.status_code != 200:
        print(f"Failed to download {image_url}")
        return None

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=filename,
        Body=response.content,
        ContentType="image/jpeg"
    )

    return filename

def update_dynamodb(artist, title, s3_key):
    s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"

    table.update_item(
        Key={
            "artist": artist,
            "title": title
        },
        UpdateExpression="SET image_url = :url",
        ExpressionAttributeValues={
            ":url": s3_url
        }
    )

def main():
    with open("2026a2_songs.json") as f:
        data = json.load(f)

    for song in data["songs"]:
        s3_key = upload_image_to_s3(song["img_url"])

        if s3_key:
            update_dynamodb(song["artist"], song["title"], s3_key)
            print(f"Uploaded + updated: {song['title']}")

if __name__ == "__main__":
    main()