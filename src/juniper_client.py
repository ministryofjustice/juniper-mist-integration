import getpass
import requests
import json


class JuniperClient:

    def login_via_username_and_password(self, username):
        # If no username defined ask user
        if username is None:
            username = input("Enter Mist Username:")
        else:
            print('Username provided: {usr}'.format(usr=username))
        password = getpass.getpass(prompt='Enter Mist password:')
        login_url = self.base_url + "/login"
        login_payload = {'email': username, 'password': password}
        self.session.post(login_url, data=login_payload)
        mfa_headers = {
            # Include CSRF token in headers
            'X-CSRFToken': self.session.cookies.get('csrftoken.eu'),
        }
        self.session.headers.update(mfa_headers)
        mfa_code = input("Enter MFA:")
        login_response = self.session.post(
            "https://api.eu.mist.com/api/v1/login/two_factor",
            data={"two_factor": mfa_code}
        )
        if login_response.status_code == 200:
            print("Login successful")
        else:
            raise ValueError("Login was not successful: {response}".format(
                response=login_response))

    def login_via_token(self):
        token = getpass.getpass(prompt='Input the MIST API TOKEN:')
        self.headers['Authorization'] = 'Token ' + token
        request_url = self.base_url + "/self/apitokens"
        response = self.session.get(request_url, headers=self.headers)
        if response.status_code == 200:
            print("Login successful")
        else:
            raise ValueError(
                "Login was not successful via token: {response}".format(response=response))

    def __init__(self, username=None, mist_login_method=None):
        self.session = requests.Session()
        self.headers = {'Content-Type': 'application/json'}
        self.base_url = 'https://api.eu.mist.com/api/v1'

        if mist_login_method == 'token':
            self.login_via_token()
        elif mist_login_method == 'credentials':
            self.login_via_username_and_password(username)
        else:
            raise ValueError('Invalid mist_login_method: {method}'.format(
                method=mist_login_method))

    def post(self, url, payload, timeout=60):
        url = 'https://api.eu.mist.com{}'.format(url)
        session = self.session
        headers = self.headers

        print('POST {}'.format(url))
        response = session.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            print('Failed to POST')
            print('\tURL: {}'.format(url))
            print('\tPayload: {}'.format(payload))
            print('\tResponse: {} ({})'.format(
                response.text, response.status_code))
            return False

        return json.loads(response.text)

    def put(self, url, payload):
        url = 'https://api.eu.mist.com{}'.format(url)
        session = self.session
        headers = self.headers

        print('PUT {}'.format(url))
        response = session.put(url, headers=headers, json=payload)

        if response.status_code != 200:
            print('Failed to PUT')
            print('\tURL: {}'.format(url))
            print('\tPayload: {}'.format(payload))
            print('\tResponse: {} ({})'.format(
                response.text, response.status_code))
            return False

        return json.loads(response.text)
