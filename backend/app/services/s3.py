import boto3
import os
from urllib.parse import urlparse
from botocore.exceptions import ClientError

AWS_REGION = os.getenv('AWS_REGION') or os.getenv('AWS_DEFAULT_REGION') or 'us-east-1'
s3 = boto3.client('s3', region_name=AWS_REGION)
BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "")

def generate_presigned_url(image_url: str):
    """
    image_url stored in DB is:
    https://bucket.s3.amazonaws.com/filename.jpg

    We extract filename and generate secure URL
    """

    if not image_url:
        return image_url

    if not BUCKET_NAME:
        # If bucket is not configured, keep the stored URL unchanged.
        return image_url

    key = image_url.strip()

    # Keep external URLs (e.g. GitHub raw links) unchanged.
    if image_url.startswith("http://") or image_url.startswith("https://"):
        parsed = urlparse(image_url)
        host = parsed.netloc.lower()
        path = parsed.path.lstrip("/")

        bucket_host_prefix = f"{BUCKET_NAME}.s3"
        is_bucket_virtual_hosted = host == f"{BUCKET_NAME}.s3.amazonaws.com" or host.startswith(bucket_host_prefix)
        is_bucket_path_style = host.startswith("s3.") and path.startswith(f"{BUCKET_NAME}/")

        if is_bucket_virtual_hosted:
            key = path
        elif is_bucket_path_style:
            key = path.split("/", 1)[1]
        else:
            return image_url

    try:
        s3.head_object(Bucket=BUCKET_NAME, Key=key)
    except ClientError:
        # If key is not found, keep original URL instead of returning a broken presigned URL.
        return image_url

    try:
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': key
            },
            ExpiresIn=3600
        )
    except Exception:
        return image_url

    return url