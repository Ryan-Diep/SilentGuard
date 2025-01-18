import boto3
import os

def lambda_handler(event, context):
    # Get the secret from AWS Secrets Manager
    client = boto3.client("secretsmanager", region_name=os.getenv("REGION"))
    secret = client.get_secret_value(SecretId="solace-auth-token")["SecretString"]

    # Extract token from the request header
    auth_header = event["headers"].get("Authorization")
    if not auth_header:
        return {
            "statusCode": 401,
            "body": "Unauthorized: Missing Authorization Header"
        }

    # Validate the token
    if auth_header != secret:
        return {
            "statusCode": 403,
            "body": "Forbidden: Invalid Token"
        }

    # Token is valid
    return {
        "isAuthorized": True
    }
