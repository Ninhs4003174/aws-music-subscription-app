import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('login')

users = [
    {"email": "user1@test.com", "username": "user1", "password": "123"},
    {"email": "user2@test.com", "username": "user2", "password": "123"},
    {"email": "user3@test.com", "username": "user3", "password": "123"},
    {"email": "user4@test.com", "username": "user4", "password": "123"},
    {"email": "user5@test.com", "username": "user5", "password": "123"},
    {"email": "user6@test.com", "username": "user6", "password": "123"},
    {"email": "user7@test.com", "username": "user7", "password": "123"},
    {"email": "user8@test.com", "username": "user8", "password": "123"},
    {"email": "user9@test.com", "username": "user9", "password": "123"},
    {"email": "user10@test.com", "username": "user10", "password": "123"}
]

def main():
    for user in users:
        table.put_item(Item=user)
        print(f"Inserted {user['email']}")

if __name__ == "__main__":
    main()