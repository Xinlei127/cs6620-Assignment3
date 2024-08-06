import json
import logging
import boto3
import os

s3 = boto3.client('s3')
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    for record in event['Records']:
        sns_message = json.loads(record['Sns']['Message'])
        if 'Records' not in sns_message:
            continue

        # Find bucket and object key from the S3 event
        source_bucket_name = sns_message['Records'][0]['s3']['bucket']['name']
        object_key = sns_message['Records'][0]['s3']['object']['key']

        # Find the destination bucket name
        dest_bucket_name = os.getenv('DEST_BUCKET_NAME')

        # Copy the object
        the_source = {'Bucket': source_bucket_name, 'Key': object_key}
        s3.copy_object(CopySource=the_source, Bucket=dest_bucket_name, Key=object_key)

    return {
        'statusCode': 200,
        'body': json.dumps('[copier]: S3 event processed successfully')
    }
