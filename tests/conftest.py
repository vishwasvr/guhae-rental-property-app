import pytest
import boto3
import os
from moto import mock_dynamodb, mock_s3, mock_cognitoidp
from unittest.mock import MagicMock, patch
import json
from decimal import Decimal


@pytest.fixture(autouse=True)
def set_env_vars():
    """Automatically set required environment variables for all tests"""
    env_vars = {
        'DYNAMODB_TABLE_NAME': 'test-table',
        'S3_BUCKET_NAME': 'test-bucket',
        'COGNITO_USER_POOL_ID': 'test-pool-id',
        'COGNITO_CLIENT_ID': 'test-client-id',
        'AWS_REGION': 'us-east-1'
    }
    with patch.dict(os.environ, env_vars):
        yield


@pytest.fixture(scope="session")
def aws_credentials():
    """Mock AWS credentials for moto"""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture(scope="session")
def dynamodb_mock(aws_credentials):
    """Mock DynamoDB service"""
    with mock_dynamodb():
        yield boto3.resource("dynamodb", region_name="us-east-1")


@pytest.fixture(scope="session")
def s3_mock(aws_credentials):
    """Mock S3 service"""
    with mock_s3():
        yield boto3.client("s3", region_name="us-east-1")


@pytest.fixture(scope="session")
def cognito_mock(aws_credentials):
    """Mock Cognito service"""
    with mock_cognitoidp():
        yield boto3.client("cognito-idp", region_name="us-east-1")


@pytest.fixture
def test_table(dynamodb_mock):
    """Create test DynamoDB table"""
    table_name = "test-table"
    try:
        table = dynamodb_mock.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "pk", "KeyType": "HASH"},
                {"AttributeName": "sk", "KeyType": "RANGE"}
            ],
            AttributeDefinitions=[
                {"AttributeName": "pk", "AttributeType": "S"},
                {"AttributeName": "sk", "AttributeType": "S"},
                {"AttributeName": "gsi1_pk", "AttributeType": "S"},
                {"AttributeName": "gsi1_sk", "AttributeType": "S"}
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "gsi1",
                    "KeySchema": [
                        {"AttributeName": "gsi1_pk", "KeyType": "HASH"},
                        {"AttributeName": "gsi1_sk", "KeyType": "RANGE"}
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits": 5,
                        "WriteCapacityUnits": 5
                    }
                }
            ],
            BillingMode="PROVISIONED",
            ProvisionedThroughput={
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5
            }
        )
    except Exception:
        # Table might already exist, get existing table
        table = dynamodb_mock.Table(table_name)
    return table


@pytest.fixture
def test_bucket(s3_mock):
    """Create test S3 bucket"""
    bucket_name = "test-bucket"
    s3_mock.create_bucket(Bucket=bucket_name)
    return bucket_name


@pytest.fixture
def test_user_pool(cognito_mock):
    """Create test Cognito user pool"""
    response = cognito_mock.create_user_pool(PoolName="test-pool")
    user_pool_id = response["UserPool"]["Id"]

    # Create user pool client
    client_response = cognito_mock.create_user_pool_client(
        UserPoolId=user_pool_id,
        ClientName="test-client"
    )
    client_id = client_response["UserPoolClient"]["ClientId"]

    return {"user_pool_id": user_pool_id, "client_id": client_id}


@pytest.fixture
def sample_property_data():
    """Sample property data for testing"""
    return {
        "title": "Test Property",
        "description": "A beautiful test property",
        "price": 250000,
        "bedrooms": 3,
        "bathrooms": 2,
        "square_feet": 1500,
        "property_type": "house",
        "address": {
            "street_address": "123 Test St",
            "city": "Test City",
            "state": "TS",
            "zip_code": "12345"
        },
        "features": ["pool", "garage"],
        "images": ["image1.jpg", "image2.jpg"]
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "email": "test@example.com",
        "name": "Test User",
        "phone": "+1234567890"
    }


@pytest.fixture
def mock_lambda_environment(monkeypatch, test_table, test_bucket, test_user_pool):
    """Set up mock environment variables for Lambda function"""
    monkeypatch.setenv("DYNAMODB_TABLE_NAME", "test-table")
    monkeypatch.setenv("S3_BUCKET_NAME", test_bucket)
    monkeypatch.setenv("COGNITO_USER_POOL_ID", test_user_pool["user_pool_id"])
    monkeypatch.setenv("COGNITO_CLIENT_ID", test_user_pool["client_id"])
    monkeypatch.setenv("AWS_REGION", "us-east-1")


@pytest.fixture
def mock_property_item(sample_property_data, sample_user_data):
    """Create a mock property item as stored in DynamoDB"""
    return {
        "pk": "PROPERTY#test-property-id",
        "sk": "METADATA",
        "gsi1_pk": f"OWNER#{sample_user_data['email']}",
        "gsi1_sk": "PROPERTY#test-property-id",
        "property_id": "test-property-id",
        "owner_id": sample_user_data["email"],
        "title": sample_property_data["title"],
        "description": sample_property_data["description"],
        "price": Decimal(str(sample_property_data["price"])),
        "bedrooms": sample_property_data["bedrooms"],
        "bathrooms": sample_property_data["bathrooms"],
        "square_feet": sample_property_data["square_feet"],
        "property_type": sample_property_data["property_type"],
        "address": sample_property_data["address"],
        "features": sample_property_data["features"],
        "images": sample_property_data["images"],
        "created_at": "2024-01-01T00:00:00.000000",
        "updated_at": "2024-01-01T00:00:00.000000"
    }


@pytest.fixture
def mock_user_item(sample_user_data):
    """Create a mock user item as stored in DynamoDB"""
    return {
        "pk": f"USER#{sample_user_data['email']}",
        "sk": "PROFILE",
        "user_id": sample_user_data["email"],
        "email": sample_user_data["email"],
        "name": sample_user_data["name"],
        "phone": sample_user_data["phone"],
        "created_at": "2024-01-01T00:00:00.000000",
        "updated_at": "2024-01-01T00:00:00.000000"
    }


@pytest.fixture
def valid_jwt_token():
    """Mock JWT token for authenticated requests"""
    return "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwibmFtZSI6IlRlc3QgVXNlciJ9.test"


@pytest.fixture
def api_headers(valid_jwt_token):
    """Standard API headers for testing"""
    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {valid_jwt_token}",
        "Access-Control-Allow-Origin": "*"
    }


@pytest.fixture
def cors_headers():
    """CORS headers for testing"""
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
        "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
    }
