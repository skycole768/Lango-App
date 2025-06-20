import boto3
import json
import os
import logging
import uuid
import time
from boto3.dynamodb.conditions import Key, Attr

s3_client = boto3.client('s3')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
region = os.getenv('AWS_REGION', 'us-east-1')
dynamodb = boto3.resource('dynamodb', region_name=region)
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])

def add_set(event, context):
    logger.info("Starting add_set handler")

    try:
        user_id = event['queryStringParameters']['user_id']
        language = event['queryStringParameters']['language']
        logger.info(f"Received user_id: {user_id}, language: {language}")
        if not user_id or not language:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'User ID and language are required'})
            }
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
        
        logger.info(f"Received body: {body}")
        set_name = body.get('set_name')
        set_description = body.get('set_description', '')
        if not set_name:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'Set name are required'})
            }
        
        logger.info(f"Adding set: {set_name} for user: {user_id} in language: {language}")

        logger.info("Generating unique set ID")
        set_id = str(uuid.uuid4())
        logger.info(f"Generated set_id: {set_id}")

        table.put_item(
            Item={
                'PK': f'USER#{user_id}#LANGUAGE#{language}',
                'SK': f'SET#{set_id}',
                'set_name': set_name,
                'set_description': set_description,
                'created_at': int(time.time()),
                'updated_at': int(time.time())
            }
        )

        logger.info("Set added successfully")
        return {
            'statusCode': 201,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'message': 'Set added successfully', 'set_id': set_id})
        }
    except Exception as e:
        logger.error(f"Error in add_set: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'error': 'Internal Server Error'})
        }

def get_sets(event, context):
    logger.info("Starting get_sets handler")

    try:
        user_id = event['queryStringParameters']['user_id']
        language = event['queryStringParameters']['language']
        logger.info(f"Recieved user_id: {user_id}, language: {language}")
        if not user_id or not language:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'User ID and language are required'})
            }
        
        logger.info(f"Querying sets for user_id: {user_id} in language: {language}")
        response = table.query(
            KeyConditionExpression=Key('PK').eq(f'USER#{user_id}#LANGUAGE#{language}')
        )
        sets = []
        for item in response.get('Items', []):
            if item['SK'].startswith('SET#'):
                sets.append({
                    'set_id': item['SK'].split('#')[1],
                    'set_name': item.get('set_name'),
                    'set_description': item.get('set_description'),
                    'created_at': item.get('created_at'),
                    'updated_at': item.get('updated_at')
                })
        logger.info(f"Sets retrieved successfully: {sets}")

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'sets': sets}, default=str)
        }
    except Exception as e:
        logger.error(f"Error in get_sets: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'error': 'Internal Server Error'})
        }

def get_set(event, context):
    logger.info("starting get_set handler")

    try:
        user_id = event['queryStringParameters']['user_id']
        language = event['queryStringParameters']['language']
        set_id = event['queryStringParameters']['set_id']
        logger.info(f"Received user_id: {user_id}, language: {language}, set_id: {set_id}")
        if not user_id or not language or not set_id:
            return {
                'statusCode': 400,
                'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
                'body': json.dumps({'error': 'User ID, language, and set ID are required'})
            }
        logger.info(f"Querying set for user_id: {user_id}, language: {language}, set_id: {set_id}")
        response = table.get_item(
            Key={
                'PK': f'USER#{user_id}#LANGUAGE#{language}',
                'SK': f'SET#{set_id}'
            }
        )
        if 'Item' not in response:
            logger.warning(f"Set not found for user_id: {user_id}, language: {language}, set_id: {set_id}")
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'Set not found'})
            }
        set_data = response['Item']
        set_data.pop('PK', None)
        set_data.pop('SK', None)
        logger.info(f"Set data retrieved: {set_data}")

        set_description = set_data.get('set_description', '')
        set_name = set_data.get('set_name', '')
        created_at = set_data.get('created_at', '')
        updated_at = set_data.get('updated_at', '')
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'set_name': set_name, 'set_description': set_description, 'created_at': created_at, 'updated_at': updated_at}, default=str)
        }
    except Exception as e:
        logger.error(f"Error in get_set: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'error': 'Internal Server Error'})
        }
    
def edit_set(event, context):
    if event['requestContext']['http']['method'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*',
            },
            'body': json.dumps({'message': 'CORS preflight response'})
        }
    
    logger.info("starting edit_set handler")

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
        
        logger.info(f"Received body for edit_set: {body}")

        user_id = event['queryStringParameters']['user_id']
        language = event['queryStringParameters']['language']
        set_id = event['queryStringParameters']['set_id']

        logger.info(f"Received user_id: {user_id}, language: {language}, set_id: {set_id}")
        if not user_id or not language or not set_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'User ID, language, and set ID are required'})
            }
        
        set_name = body.get('set_name')
        set_description = body.get('set_description', '')
        if not set_name:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'Set name and description are required'})
            }
        
        logger.info(f"Editing set: {set_id} for user: {user_id} in language: {language}")
        response = table.update_item(
            Key={
                'PK': f'USER#{user_id}#LANGUAGE#{language}',
                'SK': f'SET#{set_id}'
            },
            UpdateExpression="SET set_name = :sn, set_description = :sd, updated_at = :ua",
            ExpressionAttributeValues={
                ':sn': set_name,
                ':sd': set_description,
                ':ua': int(time.time())
            },
            ReturnValues="UPDATED_NEW"
        )

        if 'Attributes' not in response:
            logger.warning(f"Set not found for user_id: {user_id}, language: {language}, set_id: {set_id}")
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'Set not found'})
            }
        
        updated_attributes = response.get('Attributes', {})
        logger.info(f"Set updated successfully: {updated_attributes}")
        updated_attributes.pop('PK', None)
        updated_attributes.pop('SK', None)
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({
                'message': 'Set updated successfully',
                'updated_attributes': updated_attributes
            }, default=str)
        }
    except Exception as e:
        logger.error(f"Error in edit_set: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'error': 'Internal Server Error'})
        }
    
def delete_set(event, context):
    logger.info("starting delete_set handler")

    try:
        user_id = event['queryStringParameters']['user_id']
        language = event['queryStringParameters']['language']
        set_id = event['queryStringParameters']['set_id']
        logger.info(f"Received user_id: {user_id}, language: {language}, set_id: {set_id}")
        if not user_id or not language or not set_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'User ID, language, and set ID are required'})
            }
        items_to_delete = []

        prefix = f"USER#{user_id}#LANGUAGE#{language}#SET#{set_id}"
        logger.info(f"Scanning for items with PK starting with {prefix}")

        # 1. Delete all flashcards and related items under this set
        response1 = table.scan(
            FilterExpression=Attr('PK').begins_with(prefix)
        )
        items_to_delete = response1.get('Items', [])

        # 2. Delete the set metadata itself
        logger.info(f"Scanning for set metadata with PK=USER#{user_id}#LANGUAGE#{language} and SK=SET#{set_id}")
        response2 = table.scan(
            FilterExpression=Attr('PK').eq(f'USER#{user_id}#LANGUAGE#{language}') & Attr('SK').eq(f'SET#{set_id}')
        )
        items_to_delete.extend(response2.get('Items', []))

        logger.info(f"Found total {len(items_to_delete)} items to delete for set {set_id}")

        # Delete all collected items
        for item in items_to_delete:
            pk = item['PK']
            sk = item['SK']
            logger.info(f"Deleting item with PK={pk}, SK={sk}")
            table.delete_item(Key={'PK': pk, 'SK': sk})

        logger.info(f"Successfully deleted {len(items_to_delete)} items for set {set_id} of user {user_id}")

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({
                'message': f"Deleted {len(items_to_delete)} items for set {set_id} of user {user_id}"
            })
        }
    except Exception as e:
        logger.error(f"Error in delete_set: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'error': 'Internal Server Error'})
        }