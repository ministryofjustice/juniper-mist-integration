import unittest
from unittest.mock import patch, MagicMock
from src.juniper import juniper_script, \
    warn_if_using_org_id_production, plan_of_action
from io import StringIO
from datetime import datetime
import os
import pytest
from parameterized import parameterized


class TestJuniperScript(unittest.TestCase):

    @patch('src.juniper.plan_of_action')
    @patch('src.juniper.JuniperClient')
    def test_given_successful_login_when_juniper_script_runs_post_a_site(self, mock_juniper_client, mock_plan_of_action):

        # Mock Mist API responses
        mock_post = mock_juniper_client.return_value.post
        mock_post.return_value = {'id': '123', 'name': 'TestSite'}

        mock_put = mock_juniper_client.return_value.put
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
            network_template_id='46b87163-abd2-4b08-a67f-1ccecfcfd061',
            ap_versions={"AP45": "0.12.27139", "AP32": "0.12.27139"}
        )

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

    @parameterized.expand(
        ["3e824dd6-6b37-4cc7-90bb-97d744e91175",
         "9fd50080-520d-49ec-96a0-09f263fc8a05"
         ])
    @patch('builtins.input', return_value='y')
    def test_given_production_org_id_when_user_prompted_for_input_and_user_inputs_y_then_continue_to_run(self,
                                                                                                         production_org_id,
                                                                                                         user_input
                                                                                                         ):
        result = warn_if_using_org_id_production(production_org_id)
        self.assertEqual('Continuing_with_run', result)

    @parameterized.expand(
        ["3e824dd6-6b37-4cc7-90bb-97d744e91175",
         "9fd50080-520d-49ec-96a0-09f263fc8a05"
         ])
    @patch('builtins.input', return_value='n')
    def test_given_production_org_id_when_user_prompted_for_input_and_user_inputs_n_then_sys_exit(self,
                                                                                                  production_org_id,
                                                                                                  user_input):
        with self.assertRaises(SystemExit):
            warn_if_using_org_id_production(production_org_id)

    @parameterized.expand(
        ["3e824dd6-6b37-4cc7-90bb-97d744e91175",
         "9fd50080-520d-49ec-96a0-09f263fc8a05"
         ])
    @patch('builtins.input', return_value='invalid')
    def test_given_production_org_id_when_user_prompted_for_input_and_user_inputs_invalid_then_raise_error(self,
                                                                                                           production_org_id,
                                                                                                           user_input):
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
    @patch('src.juniper.JuniperClient')
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
                           mist_login_method=None,
                           ap_versions={"AP45": "0.12.27139",
                                        "AP32": "0.12.27139"}
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


class TestPlanOfActionFunction(unittest.TestCase):

    @patch("src.juniper.BuildPayload")
    def test_plan_of_action_creates_file(self, mock_payload_processor):

        # Mocking the payload processor
        mock_processor_instance = mock_payload_processor.return_value
        mock_processor_instance.get_site_payload.return_value = {
            "hello": "test"}

        with patch('builtins.input', return_value='Y'), patch('sys.exit') as mock_exit:
            plan_of_action(mock_processor_instance)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        expected_file_name = f"../data_src/mist_plan_{timestamp}.json"
        self.assertTrue(os.path.exists(expected_file_name))
        os.remove(expected_file_name)

    @patch("src.juniper.BuildPayload")
    @patch("builtins.open")
    def test_plan_of_action_exit_on_no(self, mock_open_file, mock_payload_processor):

        # Mocking the payload processor
        mock_processor_instance = mock_payload_processor.return_value
        mock_processor_instance.get_site_payload.return_value = {
            "hello": "test"}

        with patch('builtins.input', return_value='N'), self.assertRaises(SystemExit) as cm:
            plan_of_action(mock_processor_instance)
        self.assertEqual(cm.exception.code, 0)

    @patch("src.juniper.BuildPayload")
    @patch("builtins.open")
    def test_plan_of_action_invalid_input(self, mock_open_file, mock_payload_processor):

        # Mocking the payload processor
        mock_processor_instance = mock_payload_processor.return_value
        mock_processor_instance.get_site_payload.return_value = {
            "hello": "test"}

        # Mocking the built-in input
        with patch('builtins.input', return_value='invalid_input'):
            with self.assertRaises(ValueError) as cm:
                plan_of_action(mock_processor_instance)

        self.assertEqual(str(cm.exception), 'Invalid input')
