import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # Log the event details
    logger.info("[Copier]Received event: %s", json.dumps(event, indent=2))

    # Extract bucket and object key from the S3 event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']

    # Example: Log the bucket name and object key
    logger.info(f"[Copier]Bucket: {bucket_name}")
    logger.info(f"[Copier]Object key: {object_key}")

    return {
        'statusCode': 200,
        'body': json.dumps('S3 event processed successfully')
    }
