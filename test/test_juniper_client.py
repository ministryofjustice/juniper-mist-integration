import unittest
from unittest.mock import patch, MagicMock
from src.juniper_client import JuniperClient


class TestJuniperClient(unittest.TestCase):

    # Mocking the input function to provide a static MFA code
    @patch('getpass.getpass', return_value='password')
    @patch('builtins.input', return_value='123456')
    @patch('src.juniper_client.requests.Session.post', return_value=MagicMock(status_code=200))
    def test_login_successfully_via_username_and_password(self, mock_post, input_mfa, input_password):
        admin = JuniperClient(username='test@example.com',
                      mist_login_method='credentials')
        self.assertIsNotNone(admin)

        mock_post.assert_called_with(
            'https://api.eu.mist.com/api/v1/login/two_factor', data={'two_factor': '123456'})
        self.assertEqual(mock_post.call_count, 2)

    @patch('getpass.getpass', return_value='password')
    @patch('builtins.input', return_value='123456')
    @patch('src.juniper_client.requests.Session.post', return_value=MagicMock(status_code=400))
    def test_given_valid_username_and_password_when_post_to_api_and_non_200_status_code_received_then_raise_error_to_user(
            self, mock_post, mfa_input, password_input):
        with self.assertRaises(ValueError) as context:
            admin = JuniperClient(username='test@example.com',
                          mist_login_method='credentials')

        # Check the expected part of the exception message
        expected_error_message = "Login was not successful:"
        self.assertTrue(expected_error_message in str(context.exception))

        # Ensure the post method is called with the correct parameters
        mock_post.assert_called_with(
            'https://api.eu.mist.com/api/v1/login/two_factor',
            data={'two_factor': '123456'}
        )

        # Ensure the post method is called twice
        self.assertEqual(mock_post.call_count, 2)

    @patch('getpass.getpass', return_value='test_token')
    @patch('src.juniper_client.requests.Session')
    def test_given_valid_api_token_when_post_to_api_and_non_200_status_code_received_then_raise_error_to_user(self,
                                                                                                              mock_session,
                                                                                                              api_token):
        mock_get = mock_session.return_value.get
        mock_get.return_value = MagicMock(status_code=400)

        with self.assertRaises(ValueError) as context:
            admin = JuniperClient(mist_login_method='token')

        # Check the expected part of the exception message
        expected_error_message = "Login was not successful via token:"
        self.assertTrue(expected_error_message in str(context.exception))

        # Ensure the get method is called with the correct parameters
        expected_url = 'https://api.eu.mist.com/api/v1/self/apitokens'
        mock_get.assert_called_with(expected_url,
                                    headers={'Content-Type': 'application/json',
                                             'Authorization': 'Token test_token'}
                                    )

        self.assertEqual(mock_get.call_count, 1)


    @patch('getpass.getpass', return_value='token')
    @patch('src.juniper_client.requests.Session.get', return_value=MagicMock(status_code=200))
    @patch('src.juniper_client.requests.Session.post')
    def test_post(self, mock_post, mock_successful_login, input_api_token):
        # Set up the mock to return a response with a valid JSON payload
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"key": "value"}'
        mock_post.return_value = mock_response

        admin = JuniperClient(mist_login_method='token')
        self.assertIsNotNone(admin)

        result = admin.post('/some_endpoint', {'key': 'value'})

        self.assertEqual(mock_post.call_count, 1)

        expected_result = {'key': 'value'}
        self.assertEqual(result, expected_result)

    @patch('getpass.getpass', return_value='token')
    @patch('src.juniper_client.requests.Session.get', return_value=MagicMock(status_code=200))
    @patch('src.juniper_client.requests.Session.put')
    def test_put(self, mock_put, mock_successful_login, input_api_token):
        # Set up the mock to return a response with a valid JSON payload
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"key": "value"}'
        mock_put.return_value = mock_response

        admin = JuniperClient(mist_login_method='token')
        self.assertIsNotNone(admin)

        # Call the method being tested
        result = admin.put('/some_endpoint', {'key': 'value'})

        # Assert that the mock put method was called once
        self.assertEqual(mock_put.call_count, 1)

        # Assert that the method returns the expected result
        self.assertIsNotNone(result)
