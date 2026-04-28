import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('music')

with open('2026a2_songs.json') as f:
    data = json.load(f)

for song in data['songs']:
    table.put_item(Item={
        'artist': song['artist'],
        'title': song['title'],
        'year': song['year'],
        'album': song['album'],
        'image_url': song['img_url'],
        'song_id': f"{song['artist']}#{song['title']}"
    })