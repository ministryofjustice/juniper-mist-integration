import unittest
from unittest.mock import patch, MagicMock
from src.juniper import juniper_script, Admin
import os


class TestJuniperScript(unittest.TestCase):

    @patch('src.juniper.Admin.post')
    @patch('src.juniper.Admin.put')
    def test_juniper_script(self, mock_put, mock_post):
        # Mock Mist API responses
        mock_post.return_value = {'id': '123', 'name': 'TestSite'}
        mock_put.return_value = {'status': 'success'}

        # Sample input data
        data = [
            {'Site Name': 'TestSite', 'Site Address': '123 Main St',
             'gps': [1.23, 4.56], 'country_code': 'US', 'time_zone': 'UTC',
             'Enable GovWifi': 'true', 'Enable MoJWifi': 'false',
             'Wired NACS Radius Key': 'key1', 'GovWifi Radius Key': 'key2'}
        ]

        # Call the function
        juniper_script(data, mist_api_token='your_token', org_id='your_org_id')

        # Assertions
        mock_post.assert_called_once_with('/api/v1/orgs/your_org_id/sites', {
            'name': 'TestSite',
            'address': '123 Main St',
            'latlng': {'lat': 1.23, 'lng': 4.56},
            'country_code': 'US',
            'timezone': 'UTC'
        })

        mock_put.assert_called_once_with('/api/v1/sites/123/setting', {
            'vars': {
                'Enable GovWifi': 'true',
                'Enable MoJWifi': 'false',
                'Wired NACS Radius Key': 'key1',
                'GovWifi Radius Key': 'key2'
            }
        })


    def test_juniper_script_missing_api_token(self):
            # Test when mist_api_token is missing
            with self.assertRaises(ValueError) as cm:
                juniper_script([], org_id='your_org_id', mist_api_token=None)

            self.assertEqual(str(cm.exception), 'No authentication provided, provide mist username and password or API key')

    def test_juniper_script_missing_password(self):
        # Test when mist_api_token is missing
        with self.assertRaises(ValueError) as cm:
            juniper_script([], org_id='your_org_id', mist_username='username')

        self.assertEqual(str(cm.exception), 'No authentication provided, provide mist username and password or API key')

    def test_juniper_script_missing_username(self):
        # Test when mist_api_token is missing
        with self.assertRaises(ValueError) as cm:
            juniper_script([], org_id='your_org_id', mist_password='password')

        self.assertEqual(str(cm.exception), 'No authentication provided, provide mist username and password or API key')

    def test_juniper_script_missing_org_id(self):
        # Test when org_id is missing
        with self.assertRaises(ValueError) as cm:
            juniper_script([], org_id=None)

        self.assertEqual(str(cm.exception), 'Please provide Mist org_id')

    @patch('builtins.input', return_value='123456')  # Mocking the input function to provide a static MFA code
    @patch('src.juniper.requests.Session.post', return_value=MagicMock(status_code=200))
    def test_login_via_username_and_password(self, mock_post, mock_input):
        admin = Admin(username='test@example.com', password='password')
        self.assertIsNotNone(admin)

        mock_post.assert_called_with('https://api.eu.mist.com/api/v1/login/two_factor', data={'two_factor': '123456'})
        self.assertEqual(mock_post.call_count, 2)


    def test_login_via_token(self):
        admin = Admin(token='test_token')
        assert(admin.headers == {'Content-Type': 'application/json', 'Authorization': 'Token test_token'})


    @patch('src.juniper.requests.Session.post')
    def test_post(self, mock_post):
        # Set up the mock to return a response with a valid JSON payload
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"key": "value"}'
        mock_post.return_value = mock_response

        admin = Admin(token='test_token')
        self.assertIsNotNone(admin)

        result = admin.post('/some_endpoint', {'key': 'value'})


        self.assertEqual(mock_post.call_count, 1)

        expected_result = {'key': 'value'}
        self.assertEqual(result, expected_result)

    @patch('src.juniper.requests.Session.put')
    def test_put(self, mock_put):
        # Set up the mock to return a response with a valid JSON payload
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"key": "value"}'
        mock_put.return_value = mock_response

        admin = Admin(token='test_token')
        self.assertIsNotNone(admin)

        # Call the method being tested
        result = admin.put('/some_endpoint', {'key': 'value'})

        # Assert that the mock put method was called once
        self.assertEqual(mock_put.call_count, 1)

        # Assert that the method returns the expected result
        self.assertIsNotNone(result)
