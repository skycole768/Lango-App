import boto3
import json
import os
import logging
from boto3.dynamodb.conditions import Key, Attr

s3_client = boto3.client('s3')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
region = os.getenv('AWS_REGION', 'us-east-1')
dynamodb = boto3.resource('dynamodb', region_name=region)
table = dynamodb.Table(os.environ['DYNAMODB_TABLE_NAME'])

def add_language(event, context):
    logger.info("Starting add_language handler")

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
        language = body.get('language')
        if not language:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                    'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
                },
                'body': json.dumps({'error': 'Language is required'})
            }
        
        language = language.strip().lower()
        logger.info(f"Processing language: {language}")

        existing = table.query(
            KeyConditionExpression=Key('PK').eq('USER#' + user_id) & Key('SK').eq('LANGUAGE#' + language)
        )
        if existing['Count'] > 0:
            return {
                'statusCode': 409,
                'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
                'body': json.dumps({'message': 'Language already exists'})
            }
        
        logger.info("Adding language to DynamoDB")
        
        response = table.put_item(
            Item={
                'PK': 'USER#' + user_id,
                'SK': 'LANGUAGE#' + language,
                'language': language
            }
        )
        logger.info(f"Language added successfully: {response}")
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'message': 'Language added successfully'})
        }
    except Exception as e:
        logger.error(f"Error in add_language: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'error': 'Internal Server Error'})
        }
    
def get_languages(event, context):
    logger.info("Starting get_languages handler")

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
        logger.info(f"Querying languages for user_id: {user_id}")

        response = table.query(
            KeyConditionExpression=Key('PK').eq('USER#' + user_id) & Key('SK').begins_with('LANGUAGE#'),
            ProjectionExpression='SK, #lang',
            ExpressionAttributeNames={
                '#lang': 'language'
            }
        )

        languages = []
        for item in response.get('Items', []):
            language = item.get('language')
            if language:
                languages.append(language)
        logger.info(f"Languages retrieved successfully: {languages}")


        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'languages': languages})
        }
    except Exception as e:
        logger.error(f"Error in get_languages: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'error': 'Internal Server Error'})
        }
    
def delete_language(event, context):
    logger.info("starting delete_language handler")

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
                'body': json.dumps({'error': 'User ID and Language are required'})
            }
        
        items_to_delete = []

        # 1. Find items where PK starts with USER#123#LANGUAGE#Korean
        prefix = f"USER#{user_id}#LANGUAGE#{language}"
        logger.info(f"Scanning for PK starting with {prefix}")
        response1 = table.scan(
            FilterExpression=Attr('PK').begins_with(prefix)
        )
        items_to_delete.extend(response1.get('Items', []))

        # 2. Find items where PK = USER#123 AND SK = LANGUAGE#Korean
        logger.info(f"Scanning for PK=USER#{user_id} and SK begins with LANGUAGE#{language}")
        response2 = table.scan(
            FilterExpression=Attr('PK').eq(f'USER#{user_id}') & Attr('SK').begins_with(f'LANGUAGE#{language}')
        )
        items_to_delete.extend(response2.get('Items', []))

        logger.info(f"Total items to delete: {len(items_to_delete)}")

        # Delete all matched items
        for item in items_to_delete:
            pk = item['PK']
            sk = item['SK']
            logger.info(f"Deleting item with PK={pk}, SK={sk}")
            table.delete_item(Key={'PK': pk, 'SK': sk})

        logger.info(f"Successfully deleted {len(items_to_delete)} items for language {language} of user {user_id}")
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({
                'message': f"Deleted {len(items_to_delete)} items for language {language} of user {user_id}"
            })
        }
    except Exception as e:
        logger.error(f'Error in delete_language: {str(e)}')
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'error': 'Internal Server Error'})
        }
    

