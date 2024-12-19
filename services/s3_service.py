import boto3
from botocore.exceptions import NoCredentialsError


class S3Service:
    @staticmethod
    def list_s3_objects(bucket_name):
        """
        List all object keys in an S3 bucket.

        :param bucket_name: Name of the S3 bucket.
        :return: List of object keys (file paths).
        """
        s3_client = boto3.client('s3')
        try:
            response = s3_client.list_objects_v2(Bucket=bucket_name)
            if 'Contents' in response:
                object_keys = [obj['Key'] for obj in response['Contents']]
                return object_keys
            else:
                print("Bucket is empty.")
                return []
        except Exception as e:
            print(f"Error: {e}")
            return []

    @staticmethod
    def generate_presigned_url(bucket_name, object_key, expiration=3600):
        """
        Generate a pre-signed URL to share an S3 object.

        :param bucket_name: Name of the S3 bucket.
        :param object_key: Key of the object in the bucket.
        :param expiration: Time in seconds for the pre-signed URL to remain valid (default: 3600 seconds).
        :return: Pre-signed URL as a string.
        """
        s3_client = boto3.client('s3')
        try:
            response = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket_name, 'Key': object_key},
                ExpiresIn=expiration
            )
            return response
        except NoCredentialsError:
            print("AWS credentials not available.")
            return None
