import json
import uuid
import boto3
import os
import re
import logging
import bcrypt
import jwt
from boto3.dynamodb.conditions import Key, Attr
import time

s3_client = boto3.client('s3')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def hash_password(password):
    if (len(password) < 8 or not re.search(r'[A-Z]', password) or not re.search(r'\d', password) or not re.search(r'[!@#$%^&*(),.?":{}|<>]', password)):
        raise ValueError("Password must be at least 8 characters long, contain an uppercase letter, a number, and a special character")
    
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def generate_user_id():
    return str(uuid.uuid4())

def generate_jwt(user_id, username):
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': int(time.time()) + 3600
    }

    token = jwt.encode(payload, os.environ['JWT_SECRET'], algorithm='HS256')
    return token

def signup(event, context):
    logger.info("Starting signup handler")

    dynamodb = boto3.resource("dynamodb", region_name=os.environ["AWS_REGION"])
    table = dynamodb.Table(os.environ["DYNAMODB_TABLE_NAME"])

    try:
        body = json.loads(event['body'])

        if not body:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'Request body is required'})
            }
        
        logger.info(f"Received body")
        
        username = body.get('username')
        password = body.get('password')
        first_name = body.get('first_name')
        last_name = body.get('last_name')
        preferred_language = body.get('preferred_language')
        logger.info(f"processed body")

        if not username or not password or not first_name or not last_name or not preferred_language: 
            return {
                'statusCode': 401,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'Missing Required Fields'})
            }
        
        username = username.lower()
        
        logger.info(f"Check if user already exists")

        response = table.query(
        IndexName='UsernameIndex',
        KeyConditionExpression=Key('username').eq(username),
        FilterExpression = Attr('SK').begins_with('PROFILE')
        )

        if response['Items']:
            return {
                'statusCode': 409,  # Conflict
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'Username already exists'})
        }

        
        
        try:
            logger.info("Attempting to hash password")
            hashed_password = hash_password(password)
            logger.info("Password hashed successfully")
        except ValueError as ve:
            logger.warning(f"Invalid password: {str(ve)}")
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': str(ve)})
            }
        
        logger.info("Hashed password, generating user ID")
        user_id = generate_user_id()
        jwt_token = generate_jwt(user_id, username)

        logger.info("Writing user to DynamoDB")

        table.put_item(
            Item={
            'PK': 'USER#' + user_id,
            'SK': 'PROFILE',
            'user_id': user_id,
            'username': username,
            'hashed_password': hashed_password,
            'first_name': first_name,
            'last_name': last_name,
            'preferred_language': preferred_language,
            'created_at': int(time.time()),
            'last_login': int(time.time())
            }
        )

        return{
            'statusCode': 201,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            }, 
            'body': json.dumps({
                'message': 'User created successfully',
                'user_id': user_id,
                'token': jwt_token,
        })
        }
    except Exception as e:
        logger.error(f"Error in signup: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'error': 'Internal Server Error'})
        }
    
def login(event, context):
    logger.info("Starting login handler")

    dynamodb = boto3.resource("dynamodb", region_name=os.environ["AWS_REGION"])
    table = dynamodb.Table(os.environ["DYNAMODB_TABLE_NAME"])
    try:
        body = json.loads(event['body'])
        if not body:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'Request body is required'})
            }
        
        logger.info(f"Received body for login")
        username = body.get('username')
        password = body.get('password')
        logger.info(f"Processed body for login")
        if not username or not password:
            return {
                'statusCode': 401,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'Missing Required Fields'})
            }
        
        username = username.lower()
        
        logger.info("Querying DynamoDB for user")
        response = table.query(
            IndexName = 'UsernameIndex',
            KeyConditionExpression = Key('username').eq(username),
            FilterExpression = Attr('SK').begins_with('PROFILE')
        )
        logger.info(f"Query response")

        if not response['Items']:
            logger.warning(f"User not found for username: {username}")
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'Invalid Username'})
            }
        
        user_item = response['Items'][0]
        hashed_password = user_item['hashed_password']
        logger.info("Checking password")
        if not bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            logger.warning(f"Invalid password for username: {username}")
            return {
                'statusCode': 401,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'Invalid Password'})
            }
        
        logger.info("Password verified, generating JWT")
        
        user_id = user_item["user_id"]
        jwt_token = generate_jwt(user_id, username)
        logger.info("JWT generated successfully")

        logger.info("Updating last login time")
        table.update_item(
            Key={
                'PK': 'USER#' + user_id,
                'SK': 'PROFILE'
            },
            UpdateExpression='SET last_login = :ll',
            ExpressionAttributeValues={
                ':ll': int(time.time())
            }
        )

        logger.info("Last login time updated successfully")

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({
                'message': "Login Successful",
                'user_id': user_id,
                'token': jwt_token
            },default=str)
        }
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'error': 'Internal Server Error'})
        }