import boto3
import json
import os
import logging
from boto3.dynamodb.conditions import Key

s3_client = boto3.client('s3')
logger = logging.getLogger()
logger.setLevel(logging.INFO)
dynamodb = boto3.resource('dynamodb')
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
        
        logger.info("Deleting language")
        response = table.delete_item(
            Key={
                'PK': 'USER#' + user_id,
                'SK': 'LANGUAGE#' + language
            }
        )

        logger.info(f"Language deleted successfully: {response}")
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
                'Access-Control-Allow-Headers': '*, Content-Type, Authorization',
            },
            'body': json.dumps({'message': 'Language deleted successfully'})
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
    

