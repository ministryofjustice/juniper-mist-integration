import unittest
from unittest.mock import patch, MagicMock
from src.juniper import juniper_script, Admin

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

    def test_juniper_script_missing_token(self):
        # Test when mist_api_token is missing
        with self.assertRaises(SystemExit) as cm:
            juniper_script([], org_id='your_org_id')

        self.assertEqual(cm.exception.code, 1)

    def test_juniper_script_missing_org_id(self):
        # Test when org_id is missing
        with self.assertRaises(SystemExit) as cm:
            juniper_script([], mist_api_token='your_token')

        self.assertEqual(cm.exception.code, 1)
