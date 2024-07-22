import json
import logging
import boto3
import os

s3 = boto3.client('s3')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # Find bucket and object key from the S3 event
    source_bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']

    # Find the destination bucket name
    dest_bucket_name = os.getenv('DEST_BUCKET_NAME')

    logger.info('[destination bucket name] = ' + dest_bucket_name)
    # Copy the object
    the_source = {'Bucket': source_bucket_name, 'Key': object_key}
    s3.copy_object(CopySource=the_source, Bucket=dest_bucket_name, Key=object_key)

    # Find the size of the object
    response = s3.head_object(Bucket=dest_bucket_name, Key=object_key)
    object_size = response['ContentLength']

    # Log the size of the object
    if 'temp' in object_key:
        logger.info({'size': object_size})

    return {
        'statusCode': 200,
        'body': json.dumps('[copier]: S3 event processed successfully')
    }
