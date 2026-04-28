import boto3

s3 = boto3.client('s3')
BUCKET_NAME = "your-bucket-name"

def generate_presigned_url(image_url: str):
    """
    image_url stored in DB is:
    https://bucket.s3.amazonaws.com/filename.jpg

    We extract filename and generate secure URL
    """

    key = image_url.split("/")[-1]

    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': BUCKET_NAME,
            'Key': key
        },
        ExpiresIn=3600
    )

    return url