import boto3
import string
import random
import time


def upload_to_s3(bucket_name, object_name, file_path):
    # Create an S3 client
    s3_client = boto3.client('s3')

    try:
        # Upload the file
        response = s3_client.put_object(
            Bucket=bucket_name,
            Key=object_name,
            Body=open(file_path, 'rb')
        )
        print("(%s) Upload Successful: %s" % (object_name, response))
    except Exception as e:
        print("Error uploading file:", e)


def generate_file(filename, size):
    with open(filename, 'w') as fp:
        for _ in range(size):
            fp.write(random.choices(string.ascii_letters, k=1)[0])


# Generate files
generate_file('project.txt', 1024)
generate_file('temp.txt', 1024)
generate_file('project_new.txt', 1024)
generate_file('temporary_data.txt', int(2.5 * 1024))
generate_file('project_new_new.txt', 1024)
generate_file('real_temporary_data.txt', 2 * 1024)

# Upload the files to S3 bucket
bucket_name = 'firststack-sourceadfc1803-j4qgkzjqvcbc'
filenames = ['project.txt', 'temp.txt', 'project_new.txt',
             'temporary_data.txt', 'project_new_new.txt',
             'real_temporary_data.txt']
for filename in filenames:
    upload_to_s3(bucket_name, filename, filename)
    time.sleep(5)
