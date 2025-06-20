import json
from unittest.mock import patch
from lambdas.auth import handler

def test_signup_success(dynamodb_mock):
    event = {
        'body': json.dumps({
            'username': 'TestUser',
            'password': 'StrongPass1#',
            'first_name': 'Test',
            'last_name': 'User',
            'preferred_language': 'English'
        })
    }

    # simulating no existing user
    with patch.object(dynamodb_mock, 'query', return_value={'Items': []}), \
         patch.object(dynamodb_mock, 'put_item', return_value=None), \
         patch('lambdas.auth.handler.generate_jwt', return_value='fake_jwt_token'): # need to create fake as func depends on jwt secret
        response = handler.signup(event, None)
        body = json.loads(response['body'])
        assert response['statusCode'] == 201
        assert 'token' in body
        assert body['message'] == 'User created successfully'

def test_signup_missing_fields(dynamodb_mock):
    event = {'body': json.dumps({'username': 'user'})}  # missing fields

    response = handler.signup(event, None)
    assert response['statusCode'] == 401
    assert 'error' in json.loads(response['body'])

def test_login_success(dynamodb_mock):
    password_hash = handler.hash_password('StrongPass1#')
    # Insert a mock user into the table
    dynamodb_mock.put_item(Item={
        'PK': 'USER#123',
        'SK': 'PROFILE',
        'user_id': '123',
        'username': 'testuser',
        'hashed_password': password_hash,
        'first_name': 'Test',
        'last_name': 'User',
        'preferred_language': 'English',
        'created_at': 1234567890,
        'last_login': 1234567890
    })

    event = {
        'body': json.dumps({
            'username': 'testuser',
            'password': 'StrongPass1#'
        })
    }

    with patch('lambdas.auth.handler.generate_jwt', return_value='fake_jwt_token'):
        response = handler.login(event, None)
        body = json.loads(response['body'])
        assert response['statusCode'] == 200
        assert 'token' in body
        assert body['message'] == 'Login Successful'

def test_login_invalid_password(dynamodb_mock):
    password_hash = handler.hash_password('StrongPass1#')
    dynamodb_mock.put_item(Item={
        'PK': 'USER#123',
        'SK': 'PROFILE',
        'user_id': '123',
        'username': 'testuser',
        'hashed_password': password_hash
    })

    event = {
        'body': json.dumps({
            'username': 'testuser',
            'password': 'WrongPass1!'
        })
    }

    response = handler.login(event, None)
    assert response['statusCode'] == 401
    assert 'error' in json.loads(response['body'])

def test_login_user_not_found(dynamodb_mock):
    event = {
        'body': json.dumps({
            'username': 'nouser',
            'password': 'SomePass1!'
        })
    }

    response = handler.login(event, None)
    assert response['statusCode'] == 404
    assert 'error' in json.loads(response['body'])

def test_signup_weak_password(dynamodb_mock):
    event = {
        'body': json.dumps({
            'username': 'weakpassuser',
            'password': 'weak',  # short and no numbers or special chars
            'first_name': 'Weak',
            'last_name': 'User',
            'preferred_language': 'English'
        })
    }

    response = handler.signup(event, None)
    body = json.loads(response['body'])
    assert response['statusCode'] == 400
    assert 'error' in body
    assert 'Password must be at least 8 characters' in body['error']

def test_signup_username_already_exists(dynamodb_mock):
    # pre-inserting the user
    dynamodb_mock.put_item(Item={
        'PK': 'USER#existing',
        'SK': 'PROFILE',
        'user_id': 'existing',
        'username': 'existinguser',
        'hashed_password': handler.hash_password('StrongPass1#'),
        'first_name': 'Existing',
        'last_name': 'User',
        'preferred_language': 'English',
        'created_at': 1234567890,
        'last_login': 1234567890
    })

    event = {
        'body': json.dumps({
            'username': 'existinguser',
            'password': 'StrongPass1#',
            'first_name': 'Test',
            'last_name': 'User',
            'preferred_language': 'English'
        })
    }

    response = handler.signup(event, None)
    body = json.loads(response['body'])
    assert response['statusCode'] == 409
    assert 'error' in body
    assert body['error'] == 'Username already exists'

def test_login_malformed_json(dynamodb_mock):
    event = {
        'body': '{bad json}'
    }

    response = handler.login(event, None)
    assert response['statusCode'] == 500
    assert 'error' in json.loads(response['body'])
