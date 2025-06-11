import json
import re
import uuid
import boto3
import os
import logging
import bcrypt
import jwt
from boto3.dynamodb.conditions import Key, Attr
import time

s3_client = boto3.client('s3')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])


def hash_password(password):
    if len(password) < 8 or not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValueError("Password must be at least 8 characters long and contain special characters")
    
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
    try:
        body = json.loads(event['body'])
        username = body.get('username')
        password = body.get('password')
        first_name = body.get('first_name')
        last_name = body.get('last_name')

        if not username or not password or not first_name or not last_name: 
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Missing Required Fields'})
            }
        
        hashed_password = hash_password(password)
        user_id = generate_user_id()
        jwt_token = generate_jwt(user_id, username)

        user_data = {
            'user_id': user_id,
            'username': username,
            'hashed_password': hashed_password,
            'first_name': first_name,
            'last_name': last_name
        }

        table.put_item(
            Item={
            'PK': 'USER#' + user_id,
            'SK': 'PROFILE',
            'user_id': user_id,
            'username': username,
            'hashed_password': hashed_password,
            'first_name': first_name,
            'last_name': last_name
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
                'message': 'User created sucessfully',
                'user_id': user_id,
                'token': jwt_token,
        })
        }
    except Exception as e:
        logger.error(f"Error in signup: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }
    
def login(event, context):
    try:
        body = json.loads(event['body'])
        username = body.get('username')
        password = body.get('password')
        if not username or not password:
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Missing Required Fields'})
            }
        response = table.query(
            IndexName = 'UsernameIndex',
            KeyConditionExpression = Key('username').eq(username),
            FilterExpression = Attr('SK').begins_with('PROFILE')
        )

        if not response['Items']:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Invalid Username'})
            }
        
        user_item = response['Items'][0]
        hashed_password = user_item['hashed_password']
        if not bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            return {
                'statusCode': 401,
                'body': json.dumps({'error': 'Invalid Password'})
            }
        
        user_id = user_item["user_id"]
        jwt_token = generate_jwt(user_id, username)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': "Login Sucessful",
                'user_id': user_id,
                'token': jwt_token
            })
        }
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal Server Error'})
        }