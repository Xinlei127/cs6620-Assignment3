import json
import logging
import boto3

s3 = boto3.client('s3')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Find the destination bucket name
dest_bucket_name = None


def find_destination_bucket_name():
    global dest_bucket_name
    # List all buckets
    buckets = s3.list_buckets()
    for bucket in buckets['Buckets']:
        bucket_name = bucket['Name']


def lambda_handler(event, context):
    # Find bucket and object key from the S3 event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']

    # Find the destination bucket name
    if dest_bucket_name is None:
        find_destination_bucket_name()

    # Copy the object
    the_source = {'Bucket': bucket_name, 'Key': object_key}
    s3.copy_object(CopySource=the_source, Bucket=dest_bucket_name, Key=object_key)

    return {
        'statusCode': 200,
        'body': json.dumps('S3 event processed successfully')
    }
