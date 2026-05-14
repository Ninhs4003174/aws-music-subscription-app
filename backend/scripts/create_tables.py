import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.client('dynamodb')

def create_login_table():
    dynamodb.create_table(
        TableName='login',
        KeySchema=[
            {'AttributeName': 'email', 'KeyType': 'HASH'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'email', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )

def create_music_table():
    dynamodb.create_table(
        TableName='music',
        KeySchema=[
            {'AttributeName': 'artist', 'KeyType': 'HASH'},
            {'AttributeName': 'title', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'artist', 'AttributeType': 'S'},
            {'AttributeName': 'title', 'AttributeType': 'S'},
            {'AttributeName': 'year', 'AttributeType': 'S'}
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'artist-year-index',
                'KeySchema': [
                    {'AttributeName': 'artist', 'KeyType': 'HASH'},
                    {'AttributeName': 'year', 'KeyType': 'RANGE'}
                ],
                'Projection': {'ProjectionType': 'ALL'}
            }
        ],
        LocalSecondaryIndexes=[
            {
                'IndexName': 'artist-year-lsi',
                'KeySchema': [
                    {'AttributeName': 'artist', 'KeyType': 'HASH'},
                    {'AttributeName': 'year', 'KeyType': 'RANGE'}
                ],
                'Projection': {'ProjectionType': 'ALL'}
            }
        ],
        BillingMode='PAY_PER_REQUEST'
    )

def create_subscription_table():
    dynamodb.create_table(
        TableName='subscriptions',
        KeySchema=[
            {'AttributeName': 'user_email', 'KeyType': 'HASH'},
            {'AttributeName': 'song_id', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'user_email', 'AttributeType': 'S'},
            {'AttributeName': 'song_id', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )

def safe_create(func):
    try:
        func()
    except ClientError as e:
        if e.response['Error']['Code'] != 'ResourceInUseException':
            raise


safe_create(create_login_table)
safe_create(create_music_table)
safe_create(create_subscription_table)