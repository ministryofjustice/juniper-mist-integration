import unittest
from unittest.mock import patch, MagicMock
from src.juniper import juniper_script, Admin, check_if_we_need_to_append_gov_wifi_or_moj_wifi_site_groups, \
    warn_if_using_org_id_production, plan_of_action
from io import StringIO
from datetime import datetime
import os


class TestJuniperScript(unittest.TestCase):

    @patch('src.juniper.plan_of_action')
    @patch('getpass.getpass', return_value='token')
    @patch('src.juniper.requests.Session.get', return_value=MagicMock(status_code=200))
    @patch('src.juniper.Admin.post')
    @patch('src.juniper.Admin.put')
    def test_juniper_script(self, mock_put, mock_post, mock_successful_login, api_token, mock_plan_of_action):
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
            mist_login_method='token',
            org_id='your_org_id',
            site_group_ids='{"moj_wifi": "foo","gov_wifi": "bar"}',
            rf_template_id='8542a5fa-51e4-41be-83b9-acb416362cc0',
            network_template_id='46b87163-abd2-4b08-a67f-1ccecfcfd061'
        )

        # Assertions
        mock_post.assert_called_once_with('/api/v1/orgs/your_org_id/sites',
                                          {'name': 'TestSite', 'address': '123 Main St',
                                           'latlng': {'lat': 1.23, 'lng': 4.56}, 'country_code': 'US',
                                           'rftemplate_id': '8542a5fa-51e4-41be-83b9-acb416362cc0',
                                           'networktemplate_id': '46b87163-abd2-4b08-a67f-1ccecfcfd061',
                                           'timezone': 'UTC', 'sitegroup_ids': []})

    def test_juniper_script_missing_site_group_ids(self):
        with self.assertRaises(ValueError) as cm:
            juniper_script([], org_id='your_org_id', mist_login_method='token')

        self.assertEqual(str(cm.exception),
                         'Must provide site_group_ids for GovWifi & MoJWifi')

    def test_juniper_script_missing_rf_template_id(self):
        # Test when rf_template_id is missing
        with self.assertRaises(ValueError) as cm:
            juniper_script([],
                           org_id='your_org_id',
                           mist_login_method='token',
                           site_group_ids={
                               'moj_wifi': '0b33c61d-8f51-4757-a14d-29263421a904',
                               'gov_wifi': '70f3e8af-85c3-484d-8d90-93e28b911efb'},
                           network_template_id='46b87163-abd2-4b08-a67f-1ccecfcfd061'
                           )

        self.assertEqual(str(cm.exception), 'Must define rf_template_id')

    @patch('builtins.input', return_value='y')
    def test_given_production_org_id_when_user_prompted_for_input_and_user_inputs_y_then_continue_to_run(self,
                                                                                                         user_input):
        production_org_id = '3e824dd6-6b37-4cc7-90bb-97d744e91175'
        result = warn_if_using_org_id_production(production_org_id)
        self.assertEqual(result, 'Continuing_with_run')

    @patch('builtins.input', return_value='n')
    def test_given_production_org_id_when_user_prompted_for_input_and_user_inputs_n_then_sys_exit(self, user_input):
        production_org_id = '3e824dd6-6b37-4cc7-90bb-97d744e91175'
        with self.assertRaises(SystemExit):
            warn_if_using_org_id_production(production_org_id)

    @patch('builtins.input', return_value='invalid')
    def test_given_production_org_id_when_user_prompted_for_input_and_user_inputs_invalid_then_raise_error(self,
                                                                                                           user_input):
        production_org_id = '3e824dd6-6b37-4cc7-90bb-97d744e91175'
        with self.assertRaises(ValueError) as cm:
            warn_if_using_org_id_production(production_org_id)

        self.assertEqual(str(cm.exception), 'Invalid input')

    def test_juniper_script_missing_network_template_id(self):
        # Test when network_template_id is missing
        with self.assertRaises(ValueError) as cm:
            juniper_script([],
                           org_id='your_org_id',
                           mist_login_method='token',
                           site_group_ids={
                               'moj_wifi': '0b33c61d-8f51-4757-a14d-29263421a904',
                               'gov_wifi': '70f3e8af-85c3-484d-8d90-93e28b911efb'},
                           rf_template_id='46b87163-abd2-4b08-a67f-1ccecfcfd061'
                           )

        self.assertEqual(str(cm.exception), 'Must define network_template_id')

    @patch('src.juniper.plan_of_action')
    @patch('src.juniper.Admin')
    def test_given_mist_login_method_not_defined_then_default_to_credentials(self, mock_admin, mock_plan_of_action):
        output_buffer = StringIO()
        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            juniper_script([],
                           org_id='your_org_id',
                           site_group_ids={
                               'moj_wifi': '0b33c61d-8f51-4757-a14d-29263421a904',
                               'gov_wifi': '70f3e8af-85c3-484d-8d90-93e28b911efb'},
                           rf_template_id='46b87163-abd2-4b08-a67f-1ccecfcfd061',
                           network_template_id='46b87163-abd2-4b08-a67f-1ccecfcfd061',
                           mist_login_method=None
                           )
            actual_output = mock_stdout.getvalue()
        expected_message = "mist_login_method not defined. Defaulting to credentials"
        self.assertIn(expected_message, actual_output,
                      f"Output should contain: '{expected_message}'")

    def test_juniper_script_missing_org_id(self):
        # Test when org_id is missing
        with self.assertRaises(ValueError) as cm:
            juniper_script([], org_id=None)

        self.assertEqual(str(cm.exception), 'Please provide Mist org_id')

    # Mocking the input function to provide a static MFA code
    @patch('getpass.getpass', return_value='password')
    @patch('builtins.input', return_value='123456')
    @patch('src.juniper.requests.Session.post', return_value=MagicMock(status_code=200))
    def test_login_successfully_via_username_and_password(self, mock_post, input_mfa, input_password):
        admin = Admin(username='test@example.com',
                      mist_login_method='credentials')
        self.assertIsNotNone(admin)

        mock_post.assert_called_with(
            'https://api.eu.mist.com/api/v1/login/two_factor', data={'two_factor': '123456'})
        self.assertEqual(mock_post.call_count, 2)

    @patch('getpass.getpass', return_value='password')
    @patch('builtins.input', return_value='123456')
    @patch('src.juniper.requests.Session.post', return_value=MagicMock(status_code=400))
    def test_given_valid_username_and_password_when_post_to_api_and_non_200_status_code_received_then_raise_error_to_user(
            self, mock_post, mfa_input, password_input):
        with self.assertRaises(ValueError) as context:
            admin = Admin(username='test@example.com',
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
    @patch('src.juniper.requests.Session')
    def test_given_valid_api_token_when_post_to_api_and_non_200_status_code_received_then_raise_error_to_user(self,
                                                                                                              mock_session,
                                                                                                              api_token):
        mock_get = mock_session.return_value.get
        mock_get.return_value = MagicMock(status_code=400)

        with self.assertRaises(ValueError) as context:
            admin = Admin(mist_login_method='token')

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
    @patch('src.juniper.requests.Session.get', return_value=MagicMock(status_code=200))
    @patch('src.juniper.requests.Session.post')
    def test_post(self, mock_post, mock_successful_login, input_api_token):
        # Set up the mock to return a response with a valid JSON payload
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"key": "value"}'
        mock_post.return_value = mock_response

        admin = Admin(mist_login_method='token')
        self.assertIsNotNone(admin)

        result = admin.post('/some_endpoint', {'key': 'value'})

        self.assertEqual(mock_post.call_count, 1)

        expected_result = {'key': 'value'}
        self.assertEqual(result, expected_result)

    @patch('getpass.getpass', return_value='token')
    @patch('src.juniper.requests.Session.get', return_value=MagicMock(status_code=200))
    @patch('src.juniper.requests.Session.put')
    def test_put(self, mock_put, mock_successful_login, input_api_token):
        # Set up the mock to return a response with a valid JSON payload
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"key": "value"}'
        mock_put.return_value = mock_response

        admin = Admin(mist_login_method='token')
        self.assertIsNotNone(admin)

        # Call the method being tested
        result = admin.put('/some_endpoint', {'key': 'value'})

        # Assert that the mock put method was called once
        self.assertEqual(mock_put.call_count, 1)

        # Assert that the method returns the expected result
        self.assertIsNotNone(result)

    @patch('src.juniper.Admin.get_ap_versions')
    def test_ap_versions_handling(self, mock_get_ap_versions):
        # Set up a valid AP_VERSIONS environment variable
        valid_ap_versions = {"AP45": "0.12.27139", "AP32": "0.12.27139"}
        mock_get_ap_versions.return_value = valid_ap_versions

        # Test if juniper_script or Admin class handles valid AP_VERSIONS correctly
        self.assertEqual(Admin.get_ap_versions(), valid_ap_versions)

    @patch.dict('os.environ', {'AP_VERSIONS': 'Invalid JSON'})
    def test_invalid_ap_versions_handling(self):
        # Test with invalid AP_VERSIONS
        with self.assertRaises(ValueError) as cm:
        git add
            Admin.get_ap_versions()
        self.assertEqual(str(cm.exception),'Invalid AP_VERSIONS')


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
        result = check_if_we_need_to_append_gov_wifi_or_moj_wifi_site_groups(
            gov_wifi, moj_wifi, self.site_group_ids)
        self.assertEqual(result, [self.site_group_ids['gov_wifi']])

    def test_append_moj_wifi(self):
        gov_wifi = 'FALSE'
        moj_wifi = 'TRUE'
        result = check_if_we_need_to_append_gov_wifi_or_moj_wifi_site_groups(
            gov_wifi, moj_wifi, self.site_group_ids)
        self.assertEqual(result, [self.site_group_ids['moj_wifi']])

    def test_append_both_wifi(self):
        gov_wifi = 'TRUE'
        moj_wifi = 'TRUE'
        result = check_if_we_need_to_append_gov_wifi_or_moj_wifi_site_groups(
            gov_wifi, moj_wifi, self.site_group_ids)
        expected_result = [self.site_group_ids['moj_wifi'],
                           self.site_group_ids['gov_wifi']]
        self.assertEqual(result, expected_result)

    def test_append_neither_wifi(self):
        gov_wifi = 'FALSE'
        moj_wifi = 'FALSE'
        result = check_if_we_need_to_append_gov_wifi_or_moj_wifi_site_groups(
            gov_wifi, moj_wifi, self.site_group_ids)
        self.assertEqual(result, [])


class TestPlanOfActionFunction(unittest.TestCase):

    def setUp(self):
        self.data = {'Site Name': 'TestSite', 'Site Address': '123 Main St',
                     'gps': [1.23, 4.56], 'country_code': 'US', 'time_zone': 'UTC',
                     'Enable GovWifi': 'true', 'Enable MoJWifi': 'false',
                     'Wired NACS Radius Key': 'key1', 'GovWifi Radius Key': 'key2'},
        self.rf_template_id = "rf_template_id",
        self.network_template_id = "network_template_id",
        self.site_group_ids = '{"moj_wifi": "foo","gov_wifi": "bar"}'

    def test_plan_of_action_creates_file(self):
        with patch('builtins.input', return_value='Y'), patch('sys.exit') as mock_exit:
            plan_of_action(self.data, self.rf_template_id,
                           self.network_template_id, self.site_group_ids)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        expected_file_name = f"../data_src/mist_plan_{timestamp}.json"
        self.assertTrue(os.path.exists(expected_file_name))
        os.remove(expected_file_name)

    @patch("builtins.open")
    def test_plan_of_action_exit_on_no(self, mock_open_file):
        with patch('builtins.input', return_value='N'), self.assertRaises(SystemExit) as cm:
            plan_of_action(self.data, self.rf_template_id,
                           self.network_template_id, self.site_group_ids)
        self.assertEqual(cm.exception.code, 0)

    @patch("builtins.open")
    def test_plan_of_action_invalid_input(self, mock_open_file):
        with patch('builtins.input', return_value='invalid_input'), self.assertRaises(ValueError) as cm:
            plan_of_action(self.data, self.rf_template_id,
                           self.network_template_id, self.site_group_ids)
        self.assertEqual(str(cm.exception), 'Invalid input')
