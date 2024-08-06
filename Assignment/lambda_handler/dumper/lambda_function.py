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

        # Find the size of the object
        response = s3.head_object(Bucket=source_bucket_name, Key=object_key)
        object_size = response['ContentLength']

        # Log the size of the object
        if 'temp' in object_key:
            logger.info(json.dumps({'size': object_size, 'type': 'temp'}))
        else:
            logger.info(json.dumps({'size': object_size, 'type': 'regular'}))

    return {
        'statusCode': 200,
        'body': json.dumps('[dumper]: S3 event processed successfully')
    }
