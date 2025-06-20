import pytest
from moto import mock_aws
import boto3
import os
os.environ['DYNAMODB_TABLE_NAME'] = 'LangoApp'
os.environ['JWT_SECRET'] = 'testsecret'

from lambdas.auth import handler

@pytest.fixture(scope="function")
def dynamodb_mock():
    with mock_aws(config={"dynamodb": {}}):

        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='LangoApp',
            KeySchema=[
                {'AttributeName': 'PK', 'KeyType': 'HASH'},
                {'AttributeName': 'SK', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'PK', 'AttributeType': 'S'},
                {'AttributeName': 'SK', 'AttributeType': 'S'},
                {'AttributeName': 'username', 'AttributeType': 'S'}
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'UsernameIndex',
                    'KeySchema': [{'AttributeName': 'username', 'KeyType': 'HASH'}],
                    'Projection': {'ProjectionType': 'ALL'},
                    'ProvisionedThroughput': {'ReadCapacityUnits': 1, 'WriteCapacityUnits': 1}
                }
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 2, 'WriteCapacityUnits': 2}
        )

        table.meta.client.get_waiter('table_exists').wait(TableName='LangoApp')
        yield table

