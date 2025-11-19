# app/utils/s3.py
import os
import time
import uuid
import boto3
from botocore.exceptions import ClientError

AWS_REGION = os.environ.get("AWS_REGION", "us-east-2")
BUCKET = os.environ.get("AWS_S3_BUCKET")  # yennypy-books
UPLOAD_FOLDER = os.environ.get("S3_UPLOAD_FOLDER", "books")

s3_client = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY")
)

def _make_s3_key(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower()
    uid = uuid.uuid4().hex
    ts = int(time.time())
    return f"{UPLOAD_FOLDER}/{uid}_{ts}.{ext}"

def upload_fileobj_to_s3(fileobj, filename) -> str:
    s3_client = get_s3_client()
    config = _get_s3_config()
    
    key = _make_s3_key(filename)
    
    try:
        s3_client.upload_fileobj(
            Fileobj=fileobj,
            Bucket=config['BUCKET'],
            Key=key,
            ExtraArgs={"ACL": "public-read", "ContentType": fileobj.content_type}
        )
        
        s3_url = f"https://{config['BUCKET']}.s3.{config['REGION']}.amazonaws.com/{key}"
        return s3_url # Retorna la URL completa
        
    except ClientError as e:
        return None

def generate_presigned_url_for_key(key: str, expires_in: int = 3600) -> str:

    try:
        return s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET, "Key": key},
            ExpiresIn=expires_in
        )
    except ClientError:
        return None

def delete_s3_key(key: str) -> bool:
    try:
        s3_client.delete_object(Bucket=BUCKET, Key=key)
        return True
    except ClientError:
        return False
