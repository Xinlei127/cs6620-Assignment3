import json
import logging
import boto3
import os

s3 = boto3.client('s3')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # Find the destination bucket name
    dest_bucket_name = os.getenv('DEST_BUCKET_NAME')

    # List objects with prefix
    response = s3.list_objects_v2(Bucket=dest_bucket_name)

    if 'Contents' in response:
        # Find the oldest object with substring "temp"
        oldest_object = None
        for item in response['Contents']:
            if 'temp' not in item['Key']:
                continue
            if oldest_object is None or item['LastModified'] < oldest_object['LastModified']:
                oldest_object = item

        if oldest_object:
            # Delete this object
            s3.delete_object(Bucket=dest_bucket_name, Key=oldest_object['Key'])
            object_size = oldest_object['Size']
            # Log a negative size in order to get correct metric
            logger.info(f"-{object_size}")

    return {
        'statusCode': 200,
        'body': json.dumps('[cleaner]: S3 event processed successfully')
    }
