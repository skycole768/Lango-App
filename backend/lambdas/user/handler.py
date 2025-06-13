import json
import boto3
import os
import logging
from boto3.dynamodb.conditions import Key, Attr

s3_client = boto3.client('s3')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])

def get_user(event, context):
    logger.info("starting get_user handler")

    try:
        user_id = event['pathParameters']['user_id']
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
        
        response = table.get_item(
            Key={
                'PK': 'USER#' + user_id,
                'SK': 'PROFILE'
            }
        )

        if not response['Items']:
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'User not found'})
            }
        
        user_data = response['items'][0]
        logger.info(f"User data retrieved: {user_data}")
        user_data.pop('hashed_password', None)
        user_data.pop('SK', None)
        user_data.pop('PK', None)

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps(user_data)
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

        user_id = event['pathParameters']['user_id']
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
            })
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
        user_id = event['pathParameters']['user_id']
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
            key = {
                'PK': 'USER#' + user_id,
                'SK': 'PROFILE'
        },
        ConditionExpression = "attribute_exists(PK) AND attribute_exists(SK)",
        ReturnValues="ALL_OLD"
        )

        deleted_attributes = response.get('Attributes', {})
        logger.info(f"User deleted successfully: {response}")

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
            })
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
        
    
