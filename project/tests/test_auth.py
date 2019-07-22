# project/tests/test_auth.py

import unittest
import time

from project.server import db
from project.server.models import User, BlacklistToken
from project.tests.base import BaseTestCase

import json

def register_user(self, email, password):
    return self.client.post(
        '/auth/register',
        data=json.dumps(dict(
            email=email,
            password=password
        )),
        content_type='application/json'
    )

def login_user(self, email, password):
    return self.client.post(
        '/auth/login',
        data=json.dumps(dict(
            email=email,
            password=password
        )),
        content_type='application/json'
    )

def logout_user(self, token):
    return self.client.post(
        '/auth/logout',
        headers=dict( Authorization='Bearer ' + token )
    )

def get_status(self, token):
    return self.client.get(
        '/auth/status',
        headers=dict( Authorization='Bearer ' + token )
    )

class TestAuthBlueprint(BaseTestCase):
    def test_registration(self):
        """ Test for user registration """
        with self.client:
            response = register_user(self, 'joe@example.com', '$ecr3tC0d3')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully registered.')
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 201)

    def test_decode_auth_token(self):
        """ Test the decode_auth_token function """
        user = User(
            email='joe@example.com',
            password='$ecr3tC0d3'
        )
        db.session.add(user)
        db.session.commit()
        auth_token = user.encode_auth_token(user.id)
        self.assertTrue(isinstance(auth_token, bytes))
        self.assertTrue(user.decode_auth_token(auth_token.decode("utf-8")) == 1)

    def test_invalid_auth_token(self):
        """ Test the decode_auth_token function with an invalid token """
        user = User(
            email='joe@example.com',
            password='$ecr3tC0d3'
        )
        db.session.add(user)
        db.session.commit()
        auth_token = "ew0KICAiYWxnIjogIkhTMjU2IiwNCiAgInR5cCI6ICJKV1QiDQp9.ew0KICAiZW1waWQiOiAiMDAwMSIsDQogICJlbWFpbCI6ICJwcmF2ZWVuLnJAZ21haWwuY29tIiwNCiAgImZpcnN0bmFtZSI6ICJwcmF2ZWVuIiwNCiAgImxhc3RuYW1lIjogInIiLA0KICAic3ViIjogInByYXZlZW4uciIsDQogICJhdWQiOiAiaHR0cDovL3ByYXZlZW5yZW5nYXJhamFuLmNvbSIsDQogICJyb2xlcyI6ICJ7fSIsDQogICJuYmYiOiAxNTM3MzU2NDUzLA0KICAiZXhwIjogMTUzNzk2MTI1MywNCiAgImlhdCI6IDE1MzczNTY0NTMsDQogICJpc3MiOiAiaHR0cHM6Ly9wcmF2ZWVucmVuZ2FyYWphbi5jb20iDQp9.Gurbz9eHisFgydIw-XuoaNXO38z4z9AOr5BBdqg0fWw".encode('utf-8')
        self.assertTrue(isinstance(auth_token, bytes))
        self.assertTrue(user.decode_auth_token(auth_token.decode('utf-8')) == 'Invalid token.  Please log in again.')

    def test_registered_with_already_registered_user(self):
        """ Test registration with already registered email """
        user = User(
            email='joe@example.com',
            password='test'
            )
        db.session.add(user)
        db.session.commit()
        with self.client:
            response = register_user(self, 'joe@example.com', 'test')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'User already exists, please log in.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 202)

    def test_registered_user_login(self):
        """ Test for login of registered user """
        with self.client:
            # user registration
            resp_register = register_user(self, 'joe@example.com', '$ecr3tC0d3')
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)

            # registered user login
            response = login_user(self, 'joe@example.com', '$ecr3tC0d3')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully logged in.')
            self.assertTrue(data['auth_token'])
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 200)

    def test_registered_user_bad_password_login(self):
        """ Test for login of registered user with bad password """
        with self.client:
            # user registration
            resp_register = register_user(self, 'joe@example.com', '$ecr3tC0d3')
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)

            # login with incorrect password
            response = login_user(self, 'joe@example.com', 'badpassword')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Login credentials not recognised.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 401)

    def test_non_registered_user_login(self):
        """ Test for login of non-registered user """
        with self.client:
            response = login_user(self, 'bill.gates@microsoft.com', 'P@55w0rd1')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'User does not exist.')
            self.assertTrue(response.content_type == 'application/json')
            self.assertEqual(response.status_code, 404)

    def test_user_status(self):
        """ Test for user status """
        with self.client:
            # register user
            resp_register = register_user(self, 'joe@example.com', '$ecr3tC0d3')
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)
            # get user status
            token = json.loads(resp_register.data.decode())['auth_token']
            response = get_status(self, token)
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['data'] is not None)
            self.assertTrue(data['data']['email'] == 'joe@example.com')
            self.assertTrue(data['data']['admin'] is 'true' or 'false')
            self.assertEqual(response.status_code, 200)

    def test_valid_logout(self):
        """ Test for logout before token expires """
        with self.client:
            # user registration
            resp_register = register_user(self, 'joe@example.com', '$ecr3tC0d3')
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)

            # user login
            resp_login = login_user(self, 'joe@example.com', '$ecr3tC0d3')
            data_login = json.loads(resp_login.data.decode())
            self.assertTrue(data_login['status'] == 'success')
            self.assertTrue(data_login['message'] == 'Successfully logged in.')
            self.assertTrue(data_login['auth_token'])
            self.assertTrue(resp_login.content_type == 'application/json')
            self.assertEqual(resp_login.status_code, 200)

            # valid token logout
            token = json.loads(resp_login.data.decode())['auth_token']
            response = logout_user(self, token)
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'Successfully logged out.')
            self.assertEqual(response.status_code, 200)

    def test_expired_logout(self):
        """ Test for logout after token expires """
        with self.client:
            # user registration
            resp_register = register_user(self, 'joe@example.com', '$ecr3tC0d3')
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)
            # user login
            resp_login = login_user(self, 'joe@example.com', '$ecr3tC0d3')
            data_login = json.loads(resp_login.data.decode())
            self.assertTrue(data_login['status'] == 'success')
            self.assertTrue(data_login['message'] == 'Successfully logged in.')
            self.assertTrue(data_login['auth_token'])
            self.assertTrue(resp_login.content_type == 'application/json')
            self.assertEqual(resp_login.status_code, 200)
            # invalid token logout
            token = json.loads(resp_login.data.decode())['auth_token']
            time.sleep(6)
            response = logout_user(self, token)
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Signature expired.  Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_valid_blacklisted_token_logout(self):
        """ Test for logout after a valid token gets blacklisted """
        with self.client:
            # user registration
            resp_register = register_user(self, 'joe@example.com', '$ecr3tC0d3')
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)
            # user login
            resp_login = login_user(self, 'joe@example.com', '$ecr3tC0d3')
            data_login = json.loads(resp_login.data.decode())
            self.assertTrue(data_login['status'] == 'success')
            self.assertTrue(data_login['message'] == 'Successfully logged in.')
            self.assertTrue(data_login['auth_token'])
            self.assertTrue(resp_login.content_type == 'application/json')
            self.assertEqual(resp_login.status_code, 200)
            # blacklist a valid token
            blacklist_token = BlacklistToken(token=json.loads(resp_login.data.decode())['auth_token'])
            db.session.add(blacklist_token)
            db.session.commit()
            # blacklisted valid token logout
            token = json.loads(resp_login.data.decode())['auth_token']
            response = logout_user(self, token)
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Token blacklisted. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_valid_blacklisted_token_user(self):
        """ Test for user status with a blacklisted valid token """
        with self.client:
            resp_register = register_user(self, 'joe@example.com', '$ecr3tC0d3')
            data_register = json.loads(resp_register.data.decode())
            self.assertTrue(data_register['status'] == 'success')
            self.assertTrue(data_register['message'] == 'Successfully registered.')
            self.assertTrue(data_register['auth_token'])
            self.assertTrue(resp_register.content_type == 'application/json')
            self.assertEqual(resp_register.status_code, 201)
            # blacklist a valid token
            blacklist_token = BlacklistToken(token=json.loads(resp_register.data.decode())['auth_token'])
            db.session.add(blacklist_token)
            db.session.commit()
            token = json.loads(resp_register.data.decode())['auth_token']
            response = get_status(self, token)
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Token blacklisted. Please log in again.')
            self.assertEqual(response.status_code, 401)

    def test_user_status_malformed_bearer_token(self):
        """ Test for user status with malformed bearer token """
        with self.client:
            resp_register = register_user(self, 'joe@example.com', '$ecr3tC0d3')
            response = self.client.get(
                '/auth/status',
                headers=dict( Authorization='Bearer' + json.loads(resp_register.data.decode())['auth_token'] )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'fail')
            self.assertTrue(data['message'] == 'Bearer token malformed.')
            self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
