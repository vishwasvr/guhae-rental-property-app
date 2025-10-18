import boto3
from botocore.exceptions import ClientError

def upload_to_s3(file_name, bucket, object_name=None):
    if object_name is None:
        object_name = file_name

    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        print(f"Error uploading file to S3: {e}")
        return False
    return True

def save_property_to_dynamodb(table_name, property_data):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    try:
        table.put_item(Item=property_data)
    except ClientError as e:
        print(f"Error saving property to DynamoDB: {e}")
        return False
    return True

def get_property_from_dynamodb(table_name, property_id):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)

    try:
        response = table.get_item(Key={'id': property_id})
    except ClientError as e:
        print(f"Error retrieving property from DynamoDB: {e}")
        return None

    return response.get('Item')