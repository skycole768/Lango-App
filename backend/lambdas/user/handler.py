import json
import boto3
import os
import logging
import re 
import bcrypt

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


def get_user(event, context):
    logger.info("starting get_user handler")

    try:
        user_id = event['queryStringParameters']['user_id']
        logger.info(f"Received user_id: {user_id}")

        if not user_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'User ID is required'})
            }

        logger.info(f"Attempting to retrieve user with ID: {user_id}")
        
        response = table.get_item(
            Key={
                'PK': 'USER#' + user_id,
                'SK': 'PROFILE'
            }
        )

        logger.info(f"Retrieved response")

        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'User not found'})
            }
        
        user_data = response['Item']
        user_data.pop('hashed_password', None)
        user_data.pop('SK', None)
        user_data.pop('PK', None)
        logger.info(f"User data retrieved: {user_data}")

        username = user_data.get('username')
        preferred_language = user_data.get('preferred_language')
        first_name = user_data.get('first_name')
        last_name = user_data.get('last_name')
        created_at = user_data.get('created_at')
        last_login = user_data.get('last_login')

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'username': username,
                                'preferred_language': preferred_language,
                                'first_name': first_name,
                                'last_name': last_name,
                                'created_at': created_at,
                                'last_login': last_login}, 
                                default=str)
        }
    except Exception as e:
        logger.error(f'Error in get_user: {str(e)}')
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'error': 'Internal Server Error'})
        }
    
def edit_user(event, context):
    logger.info("starting edit_user handler")

    try:
        body = json.loads(event['body'])
        logger.info(f"Received body for edit_user")

        user_id = event['queryStringParameters']['user_id']
        logger.info(f"Received user_id: {user_id}")
        if not user_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'User ID is required'})
            }
        
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
        
        first_name = body.get('first_name')
        last_name = body.get('last_name')
        preferred_language = body.get('preferred_language')
        username = body.get('username')
        password = body.get('password')

        if not first_name or not last_name or not preferred_language or not username or not password:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'All fields are required'})
            }
        
        hashed_password = hash_password(password)
        logger.info("Password hashed successfully")

        response = table.update_item(
            Key={
                'PK': 'USER#' + user_id,
                'SK': 'PROFILE'
            },

            UpdateExpression="set first_name=:f, last_name=:l, preferred_language=:p, username=:u, hashed_password=:hp",
            ExpressionAttributeValues={
                ':f': first_name,
                ':l': last_name,
                ':p': preferred_language,
                ':u': username,
                ':hp': hashed_password
            },
            ReturnValues="UPDATED_NEW"
        )
        updated_attributes = response.get('Attributes', {})

        if 'Attributes' not in response:
            logger.warning(f"User with ID {user_id} not found")
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'Set not found'})
            }

        updated_attributes.pop('hashed_password', None)

        logger.info(f"User updated successfully: {response}")
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({
                'message': 'User updated successfully',
                'updated_attributes': updated_attributes
            }, default=str)
        }
    except Exception as e:
        logger.error(f'Error in edit_user: {str(e)}')
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'error': 'Internal Server Error'})
        }

def delete_user(event, context):        
    logger.info("starting delete_user handler")
    try:
        user_id = event['queryStringParameters']['user_id']
        logger.info(f"Recieved user_id: {user_id}")
        if not user_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'User ID is required'})
            }
        
        logger.info(f"Attempting to delete user with ID: {user_id}")

        response = table.delete_item(
            Key = {
                'PK': 'USER#' + user_id,
                'SK': 'PROFILE'
        },
        ConditionExpression = "attribute_exists(PK) AND attribute_exists(SK)",
        ReturnValues="ALL_OLD"
        )

        deleted_attributes = response.get('Attributes', {})
        logger.info(f"User deleted successfully: {response}")

        deleted_attributes.pop('hashed_password', None)
        deleted_attributes.pop('SK', None)
        deleted_attributes.pop('PK', None)

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({
                'message': 'User deleted successfully',
                'deleted_attributes': deleted_attributes
            }, default=str)
        }
    except Exception as e:
        logger.error(f'Error in delete_user: {str(e)}')
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'error': 'Internal Server Error'})
        }
        
    
