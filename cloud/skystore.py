import os
import boto3
from botocore.exceptions import NoCredentialsError
from config import S3_BUCKET, S3_KEY, S3_SECRET, S3_REGION, S3_ENDPOINT, UPLOAD_FOLDER

class SkyStore:
    """Hybrid storage provider (Local + S3)."""

    @staticmethod
    def get_client():
        if S3_KEY and S3_SECRET:
            return boto3.client(
                's3',
                aws_access_key_id=S3_KEY,
                aws_secret_access_key=S3_SECRET,
                region_name=S3_REGION,
                endpoint_url=S3_ENDPOINT
            )
        return None

    @staticmethod
    def save_file(user, filename, data):
        """Saves encrypted data to the preferred storage."""
        client = SkyStore.get_client()
        s3_key = f"{user}/{filename}"

        if client and S3_BUCKET:
            try:
                client.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=data)
                print(f"[CLOUD] Saved {filename} to S3 bucket {S3_BUCKET}")
                return True
            except Exception as e:
                print(f"[CLOUD ERROR] S3 Upload failed: {e}")
                # Fallback to local if S3 fails
        
        # Local fallback
        user_dir = os.path.join(UPLOAD_FOLDER, user)
        os.makedirs(user_dir, exist_ok=True)
        file_path = os.path.join(user_dir, filename)
        
        with open(file_path, "wb") as f:
            f.write(data)
        print(f"[LOCAL] Saved {filename} to {file_path}")
        return True

    @staticmethod
    def get_file_data(user, filename):
        """Retrieves file data from the preferred storage."""
        client = SkyStore.get_client()
        s3_key = f"{user}/{filename}"

        if client and S3_BUCKET:
            try:
                response = client.get_object(Bucket=S3_BUCKET, Key=s3_key)
                return response['Body'].read()
            except Exception as e:
                print(f"[CLOUD ERROR] S3 Download failed: {e}")

        # Local fallback
        file_path = os.path.join(UPLOAD_FOLDER, user, filename)
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return f.read()
        return None

    @staticmethod
    def list_files(user):
        """Lists files for a specific user."""
        client = SkyStore.get_client()
        files = []

        if client and S3_BUCKET:
            try:
                response = client.list_objects_v2(Bucket=S3_BUCKET, Prefix=f"{user}/")
                if 'Contents' in response:
                    for obj in response['Contents']:
                        # Remove user prefix
                        fname = obj['Key'].replace(f"{user}/", "", 1)
                        if fname: # Avoid empty folder entries
                            files.append(fname)
                return files
            except Exception as e:
                print(f"[CLOUD ERROR] S3 List failed: {e}")

        # Local fallback
        user_dir = os.path.join(UPLOAD_FOLDER, user)
        if os.path.exists(user_dir):
            return [f for f in os.listdir(user_dir) if os.path.isfile(os.path.join(user_dir, f))]
        return []

    @staticmethod
    def delete_file(user, filename):
        """Deletes a file from the preferred storage."""
        client = SkyStore.get_client()
        s3_key = f"{user}/{filename}"

        if client and S3_BUCKET:
            try:
                client.delete_object(Bucket=S3_BUCKET, Key=s3_key)
                return True
            except Exception as e:
                print(f"[CLOUD ERROR] S3 Delete failed: {e}")

        # Local fallback
        file_path = os.path.join(UPLOAD_FOLDER, user, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False