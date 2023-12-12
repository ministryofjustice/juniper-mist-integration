import unittest
from unittest.mock import patch, MagicMock
from src.juniper import juniper_script, Admin, check_if_we_need_to_append_gov_wifi_or_moj_wifi_site_groups


class TestJuniperScript(unittest.TestCase):

    @patch('src.juniper.requests.Session.get', return_value=MagicMock(status_code=200))
    @patch('src.juniper.Admin.post')
    @patch('src.juniper.Admin.put')
    def test_juniper_script(self, mock_put, mock_post, mock_successful_login):
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
        juniper_script(
            data,
            mist_api_token='your_token',
            org_id='your_org_id',
            site_group_ids='{"moj_wifi": "foo","gov_wifi": "bar"}'
        )

        # Assertions
        mock_post.assert_called_once_with('/api/v1/orgs/your_org_id/sites', {
            'name': 'TestSite',
            'address': '123 Main St',
            'latlng': {'lat': 1.23, 'lng': 4.56},
            'country_code': 'US',
            'rftemplate_id': '8542a5fa-51e4-41be-83b9-acb416362cc0',
            'timezone': 'UTC',
            'sitegroup_ids': []
        })

        mock_put.assert_called_once_with('/api/v1/sites/123/setting', {
            'vars': {
                'site_specific_radius_wired_nacs_secret': 'key1',
                'site_specific_radius_govwifi_secret': 'key2',
                'address' : '123 Main St',
                'site_name': 'TestSite'
            }
        })

    def test_juniper_script_missing_site_group_ids(self):
        # Test when mist_api_token is missing
        with self.assertRaises(ValueError) as cm:
            juniper_script([], org_id='your_org_id', mist_api_token='token')

        self.assertEqual(str(cm.exception), 'Must provide site_group_ids for GovWifi & MoJWifi')

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
    def test_login_successfully_via_username_and_password(self, mock_post, mock_input):
        admin = Admin(username='test@example.com', password='password')
        self.assertIsNotNone(admin)

        mock_post.assert_called_with('https://api.eu.mist.com/api/v1/login/two_factor', data={'two_factor': '123456'})
        self.assertEqual(mock_post.call_count, 2)

    @patch('builtins.input', return_value='123456')
    @patch('src.juniper.requests.Session.post', return_value=MagicMock(status_code=400))
    def test_given_valid_username_and_password_when_post_to_api_and_non_200_status_code_received_then_raise_error_to_user(self, mock_post, mock_input):
        with self.assertRaises(ValueError) as context:
            admin = Admin(username='test@example.com', password='password')

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



    @patch('src.juniper.requests.Session')
    def test_given_valid_api_token_when_post_to_api_and_non_200_status_code_received_then_raise_error_to_user(self, mock_session):
        mock_get = mock_session.return_value.get
        mock_get.return_value = MagicMock(status_code=400)

        with self.assertRaises(ValueError) as context:
            admin = Admin(token='test_token')

        # Check the expected part of the exception message
        expected_error_message = "Login was not successful via token:"
        self.assertTrue(expected_error_message in str(context.exception))

        # Ensure the get method is called with the correct parameters
        expected_url = 'https://api.eu.mist.com/api/v1/self/apitokens'
        mock_get.assert_called_with(expected_url,
                                    headers={'Content-Type': 'application/json', 'Authorization': 'Token test_token'}
                                    )

        self.assertEqual(mock_get.call_count, 1)

    @patch('src.juniper.requests.Session.get', return_value=MagicMock(status_code=200))
    @patch('src.juniper.requests.Session.post')
    def test_post(self, mock_post, mock_successful_login):
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

    @patch('src.juniper.requests.Session.get', return_value=MagicMock(status_code=200))
    @patch('src.juniper.requests.Session.put')
    def test_put(self, mock_put, mock_successful_login):
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

class TestCheckIfNeedToAppend(unittest.TestCase):

    def setUp(self):
        # Define sample site group IDs for testing
        self.site_group_ids = {
            'moj_wifi': '0b33c61d-8f51-4757-a14d-29263421a904',
            'gov_wifi': '70f3e8af-85c3-484d-8d90-93e28b911efb'
        }

    def test_append_gov_wifi(self):
        gov_wifi = 'TRUE'
        moj_wifi = 'FALSE'
        result = check_if_we_need_to_append_gov_wifi_or_moj_wifi_site_groups(gov_wifi, moj_wifi, self.site_group_ids)
        self.assertEqual(result, [self.site_group_ids['gov_wifi']])

    def test_append_moj_wifi(self):
        gov_wifi = 'FALSE'
        moj_wifi = 'TRUE'
        result = check_if_we_need_to_append_gov_wifi_or_moj_wifi_site_groups(gov_wifi, moj_wifi, self.site_group_ids)
        self.assertEqual(result, [self.site_group_ids['moj_wifi']])

    def test_append_both_wifi(self):
        gov_wifi = 'TRUE'
        moj_wifi = 'TRUE'
        result = check_if_we_need_to_append_gov_wifi_or_moj_wifi_site_groups(gov_wifi, moj_wifi, self.site_group_ids)
        expected_result = [self.site_group_ids['moj_wifi'], self.site_group_ids['gov_wifi']]
        self.assertEqual(result, expected_result)

    def test_append_neither_wifi(self):
        gov_wifi = 'FALSE'
        moj_wifi = 'FALSE'
        result = check_if_we_need_to_append_gov_wifi_or_moj_wifi_site_groups(gov_wifi, moj_wifi, self.site_group_ids)
        self.assertEqual(result, [])
