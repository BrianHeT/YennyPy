# app/utils/s3.py
import os
import time
import uuid
import boto3
from botocore.exceptions import ClientError
from flask import current_app

AWS_REGION = os.environ.get("AWS_REGION", "us-east-2")
BUCKET = os.environ.get("AWS_S3_BUCKET")  # yennypy-books
UPLOAD_FOLDER = os.environ.get("S3_UPLOAD_FOLDER", "books")

def get_s3_client():
    
    return boto3.client(
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
    key = _make_s3_key(filename)
    
    try:
        s3_client.upload_fileobj(
            Fileobj=fileobj,
            Bucket=BUCKET,
            Key=key,
            ExtraArgs={"ContentType": fileobj.content_type}  
        )
        
        
        s3_url = f"https://{BUCKET}.s3.{AWS_REGION}.amazonaws.com/{key}"
        return s3_url
        
    except ClientError as e:
        print(f"Error uploading to S3: {e}")
        return None

def generate_presigned_url_for_key(key: str, expires_in: int = 3600) -> str:
    
    s3_client = get_s3_client()
    
    try:
        return s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET, "Key": key},
            ExpiresIn=expires_in
        )
    except ClientError as e:
        print(f"Error generating presigned URL: {e}")
        return None

def delete_s3_key(key: str) -> bool:
    
    s3_client = get_s3_client()
    
    try:
        s3_client.delete_object(Bucket=BUCKET, Key=key)
        return True
    except ClientError as e:
        print(f"Error deleting from S3: {e}")
        return False