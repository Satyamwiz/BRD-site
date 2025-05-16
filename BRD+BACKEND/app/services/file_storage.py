import os
import uuid
# import boto3
# from google.cloud import storage



UPLOAD_DIR = "uploads"

class LocalFileStorage:
    def __init__(self, base_dir: str = UPLOAD_DIR):
        self.base_dir = base_dir
        os.makedirs(base_dir, exist_ok=True)

    def save(self, file_bytes: bytes, original_filename: str) -> str:
        ext = os.path.splitext(original_filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        path = os.path.join(self.base_dir, unique_name)
        with open(path, "wb") as f:
            f.write(file_bytes)
        return path

    def delete(self, path: str):
        if os.path.exists(path):
            os.remove(path)

    def read(self, path: str) -> bytes:
        with open(path, "rb") as f:
            return f.read()


class S3Storage:
    def __init__(self, bucket_name: str, region: str = "us-east-1"):
        self.bucket_name = bucket_name
        self.s3 = boto3.client("s3", region_name=region)

    def save(self, file_bytes: bytes, original_filename: str) -> str:
        ext = os.path.splitext(original_filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        key = f"uploads/{unique_name}"
        self.s3.put_object(Bucket=self.bucket_name, Key=key, Body=file_bytes, ACL="public-read")
        return f"https://{self.bucket_name}.s3.amazonaws.com/{key}"

    def delete(self, key: str):
        self.s3.delete_object(Bucket=self.bucket_name, Key=key)

    def read(self, key: str) -> bytes:
        response = self.s3.get_object(Bucket=self.bucket_name, Key=key)
        return response["Body"].read()

class GCSStorage:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def save(self, file_bytes: bytes, original_filename: str) -> str:
        ext = os.path.splitext(original_filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        blob = self.bucket.blob(f"uploads/{unique_name}")
        blob.upload_from_string(file_bytes, content_type="application/octet-stream")
        blob.make_public()
        return blob.public_url

    def delete(self, key: str):
        blob = self.bucket.blob(key)
        blob.delete()

    def read(self, key: str) -> bytes:
        blob = self.bucket.blob(key)
        return blob.download_as_bytes()
