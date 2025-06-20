import boto3
import json
import os
import logging
import uuid
import time
from boto3.dynamodb.conditions import Key

s3_client = boto3.client('s3')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
region = os.getenv('AWS_REGION', 'us-east-1')
dynamodb = boto3.resource('dynamodb', region_name=region)
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])

def add_flashcard(event, context):
    logger.info("Starting add_flashcard handler")

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

        body = json.loads(event['body'])
        logger.info(f"Received body: {body}")
        word = body.get('word')
        usage = body.get('usage')
        translated_word = body.get('translated_word')
        translated_usage = body.get('translated_usage')
        if not word or not translated_word:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'Word and translated word are required'})
            }

        logger.info(f"adding flashcard for user {user_id}, language {language}, set {set_id}")
        flashcard_id = str(uuid.uuid4())
        response = table.put_item(
            Item={
                'PK': f'USER#{user_id}#LANGUAGE#{language}#SET#{set_id}',
                'SK': f'FLASHCARD#{flashcard_id}',
                'word': word,
                'usage': usage,
                'translated_word': translated_word,
                'translated_usage': translated_usage,
                'created_at': int(time.time()), 
                'updated_at': int(time.time()),
            }
        )
        logger.info(f"Flashcard added with ID: {flashcard_id}")
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'message': 'Flashcard added successfully', 'flashcard_id': flashcard_id})
        }
    except Exception as e:
        logger.error(f"Error in add_flashcard: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'error': 'Internal Server Error'})
        }
    
def get_flashcards(event, context):
    logger.info("Starting get_flashcards handler")

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

        response = table.query(
            KeyConditionExpression=Key('PK').eq(f'USER#{user_id}#LANGUAGE#{language}#SET#{set_id}') & Key('SK').begins_with('FLASHCARD#'),
            ProjectionExpression='SK, word, #u, translated_word, #tu, created_at, updated_at',
            ExpressionAttributeNames={
                '#u': 'usage',
                '#tu': 'translated_usage'
            }
        )
        
        flashcards = []
        for item in response.get('Items', []):
            flashcard = {
                'flashcard_id': item['SK'].split('#')[1],
                'word': item.get('word'),
                'usage': item.get('usage'),
                'translated_word': item.get('translated_word'),
                'translated_usage': item.get('translated_usage'),
                'created_at': item.get('created_at'),
                'updated_at': item.get('updated_at')
            }
            flashcards.append(flashcard)
        logger.info(f"Retrieved {len(flashcards)} flashcards for user {user_id}, language {language}, set {set_id}")
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'flashcards': flashcards}, default=str)
        }
    except Exception as e:
        logger.error(f"Error in get_flashcards: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'error': 'Internal Server Error'})
        }
    
def get_flashcard(event, context):
    logger.info("Starting get_flashcard handler")

    try:
        user_id = event['queryStringParameters']['user_id']
        language = event['queryStringParameters']['language']
        set_id = event['queryStringParameters']['set_id']
        flashcard_id = event['queryStringParameters']['flashcard_id']
        logger.info(f"Received user_id: {user_id}, language: {language}, set_id: {set_id}, flashcard_id: {flashcard_id}")
        if not user_id or not language or not set_id or not flashcard_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'User ID, language, set ID, and flashcard ID are required'})
            }

        response = table.get_item(
            Key={
                'PK': f'USER#{user_id}#LANGUAGE#{language}#SET#{set_id}',
                'SK': f'FLASHCARD#{flashcard_id}'
            },
            ProjectionExpression='word, #u, translated_word, #tu, created_at, updated_at',
            ExpressionAttributeNames={
                '#u': 'usage',
                '#tu': 'translated_usage'
            }
        )
        
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'Flashcard not found'})
            }
        
        item = response['Item']
        flashcard = {
            'word': item.get('word'),
            'usage': item.get('usage'),
            'translated_word': item.get('translated_word'),
            'translated_usage': item.get('translated_usage'),
            'created_at': item.get('created_at'),
            'updated_at': item.get('updated_at')
        }
        logger.info(f"Retrieved flashcard: {flashcard}")
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'flashcard': flashcard}, default=str)
        }
    except Exception as e:
        logger.error(f"Error in get_flashcard: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'error': 'Internal Server Error'})
        }
    
def edit_flashcard(event, context):
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
    
    logger.info("Starting edit_flashcard handler")

    try:
        user_id = event['queryStringParameters']['user_id']
        language = event['queryStringParameters']['language']
        set_id = event['queryStringParameters']['set_id']
        flashcard_id = event['queryStringParameters']['flashcard_id']
        logger.info(f"Received user_id: {user_id}, language: {language}, set_id: {set_id}, flashcard_id: {flashcard_id}")
        if not user_id or not language or not set_id or not flashcard_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'User ID, language, set ID, and flashcard ID are required'})
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
        word = body.get('word')
        usage = body.get('usage')
        translated_word = body.get('translated_word')
        translated_usage = body.get('translated_usage')
        
        if not word or not usage or not translated_usage or not translated_word:
            logger.error("Missing required fields for editing flashcard")
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'Word, usage, translated word, and translated usage are required'})
            }
        logger.info(f"Editing flashcard for user {user_id}, language {language}, set {set_id}, flashcard {flashcard_id}")

        response = table.update_item(
            Key={
                'PK': f'USER#{user_id}#LANGUAGE#{language}#SET#{set_id}',
                'SK': f'FLASHCARD#{flashcard_id}'
            },
            UpdateExpression='SET word = :w, #u = :u, translated_word = :tw, #tu = :tu, updated_at = :ua',
            ExpressionAttributeNames={
                '#u': 'usage',
                '#tu': 'translated_usage'
            },
            ExpressionAttributeValues={
                ':w': word,
                ':u': usage,
                ':tw': translated_word,
                ':tu': translated_usage,
                ':ua': int(time.time())
            },
            ReturnValues='UPDATED_NEW'
        )

        if 'Attributes' not in response:
            logger.warning(f"Set not found for user_id: {user_id}, language: {language}, set_id: {set_id}, flashcard_id: {flashcard_id}")
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'Set not found'})
            }

        logger.info(f"Flashcard {flashcard_id} updated successfully")

        updated_flashcard = response['Attributes']
        flashcard = {
            'word': updated_flashcard.get('word'),
            'usage': updated_flashcard.get('usage'),
            'translated_word': updated_flashcard.get('translated_word'),
            'translated_usage': updated_flashcard.get('translated_usage'),
            'updated_at': updated_flashcard.get('updated_at')
        }

        logger.info(f"Updated flashcard: {flashcard}")
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'message': 'Flashcard updated successfully', 'flashcard': flashcard}, default=str)
        }
    except Exception as e:
        logger.error(f"Error in edit_flashcard: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'error': 'Internal Server Error'})
        }
    
def delete_flashcard(event, context):
    logger.info("Starting delete_flashcard handler")

    try:
        user_id = event['queryStringParameters']['user_id']
        language = event['queryStringParameters']['language']
        set_id = event['queryStringParameters']['set_id']
        flashcard_id = event['queryStringParameters']['flashcard_id']
        logger.info(f"Received user_id: {user_id}, language: {language}, set_id: {set_id}, flashcard_id: {flashcard_id}")
        if not user_id or not language or not set_id or not flashcard_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'User ID, language, set ID, and flashcard ID are required'})
            }

        response = table.delete_item(
            Key={
                'PK': f'USER#{user_id}#LANGUAGE#{language}#SET#{set_id}',
                'SK': f'FLASHCARD#{flashcard_id}'
            }
        )
        
        logger.info(f"Flashcard {flashcard_id} deleted successfully")
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'message': 'Flashcard deleted successfully'})
        }
    except Exception as e:
        logger.error(f"Error in delete_flashcard: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'error': 'Internal Server Error'})
        }