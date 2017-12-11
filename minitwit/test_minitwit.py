import os
import tempfile
import pytest
import requests
import json
import minitwit
#from urllib2 import urlopen



@pytest.fixture
def client():
    db_fd, minitwit.app.config['DATABASE'] = tempfile.mkstemp()
    client = minitwit.app.test_client()
    with minitwit.app.app_context():
        minitwit.init_db()

    yield client

    os.close(db_fd)
    os.unlink(minitwit.app.config['DATABASE'])


def logout(client):
    """Helper function to logout"""
    return client.get('/api/account/verify_credentials', follow_redirects=True)


def login(client, username, password):
    """Helper function to login"""
    ''' **** "query_string" is the key in arg passing in flask'''

    return client.post('/api/account/verify_credentials', query_string={
        'username': username,
        'password': password
    }, follow_redirects=True)


def test_logout(client):
    """Make sure logging out works"""
    rv = logout(client)
    json_data = rv.data
    temp = json.loads(json_data)  # typecasting string to JSON

    # print(rv.data)
    print(json.loads(rv.data))

    '''Checking error codes for assert - for logout
        200 -  Successfully logged out
        403 -  No user logged in to the system
    '''
    assert 200 == temp['error_code'] or 401 == temp['error_code']


def test_login(client):

    rv = login(client, 'akshay', 'wrongpassword')
    json_data = rv.data
    print(rv.data)
    temp = json.loads(json_data)  # typecasting string to JSON

    print(json.loads(rv.data))
    assert 401 == temp['error_code']

    result = login(client, 'wrongusername', 'Test')
    temp = json.loads(result.data)  # typecasting string to JSON
    assert 401 == temp['error_code']
'''
NOt able to maintain session, need some other way to run code which need login
'''

def add_friendship(client, username):
    """Helper function to login"""
    ''' **** "query_string" is the key in arg passing in flask'''

    return client.post('/api/friendships/create', query_string={
        'username': username

    }, follow_redirects=True)

def test_add_friendship(client):

    login(client, 'akshay', 'Test')
    rv = add_friendship(client, 'Sam')
    json_data = rv.data
    print(rv.data)
    temp = json.loads(json_data)  # typecasting string to JSON

    print(json.loads(rv.data))
    assert 200 == temp['error_code']



def add_message(client, text):
    """Records a message"""
    rv = client.post('/api/statuses/update', query_string={'message': text},
                     follow_redirects=True)

    json_data = rv.data
    temp = json.loads(json_data)
    if text:
        assert 200 == temp['error_code']
    return rv


def test_message_recording(client):
    """Check if adding messages works"""
    #url = "http://127.0.0.1:5000/api/account/verify_credentials?username=akshay&password=Test"
    # urlopen(url)

    login(client, 'akshay', 'Test')
    add_message(client, 'test message 1')
    add_message(client, '<test message 2>')
    rv = client.get('/api/statuses/public_timeline')

    json_data = rv.data
    temp = json.loads(json_data)
    assert 200 == temp['error_code']

    #print rv.data
    #assert b'test message 1' in rv.data
    #assert b'&lt;test message 2&gt;' in rv.data
