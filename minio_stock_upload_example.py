from minio import Minio
from minio.error import S3Error

def upload_file_to_minio(bucket_name, file_path, object_name):
    # Create a MinIO client with the MinIO server URL, Access Key, and Secret Key.
    minio_client = Minio(
        "localhost:9000",
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False  # Set to True if MinIO server is setup with TLS/SSL
    )

    # Make a bucket with the make_bucket API call.
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
    except S3Error as err:
        print(f"Error occurred: {err}")
        return

    # Upload the file to the bucket.
    try:
        minio_client.fput_object(
            bucket_name=bucket_name,
            object_name=object_name,
            file_path=file_path,
        )
        print(f"'{file_path}' is successfully uploaded as '{object_name}' to bucket '{bucket_name}'.")
    except S3Error as err:
        print(f"Error occurred: {err}")

if __name__ == "__main__":
    bucket_name = "my-bucket"
    file_path = "example.txt"  # Path to your file
    object_name = "example.txt"  # Object name in bucket (can be a path like 'folder/subfolder/example.txt')

    upload_file_to_minio(bucket_name, file_path, object_name)
