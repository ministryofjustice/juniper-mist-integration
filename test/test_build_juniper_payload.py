from src.build_juniper_payload import BuildPayload
import unittest
from unittest.mock import patch
import json


class TestBuildPayLoad(unittest.TestCase):

    def setUp(self):
        self.sample_data = [
            {
                'Site Name': 'MOJ-0137-Probation-Gloucestershire-TwyverHouse',
                'Site Address': 'Twyver House, Bruton Way, Gloucester, GL1 1PB',
                'gps': [51.86467215, -2.2396225106929535],
                'country_code': 'GB',
                'time_zone': 'Europe/London',
                'Enable GovWifi': 'True',
                'Enable MoJWifi': 'True',
                'GovWifi Radius Key': 'govwifi_secret',
                'Wired NACS Radius Key': 'wired_nacs_secret'
            },
            {
                'Site Name': 'Test location 2',
                'Site Address': '102 Petty France, London SW1H 9AJ',
                'gps': [51.499929300000005, -0.13477761285315926],
                'country_code': 'GB',
                'time_zone': 'Europe/London',
                'Enable GovWifi': 'False',
                'Enable MoJWifi': 'False'
            },
            {
                'Site Name': 'Test location 3',
                'Site Address': 'Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB',
                'gps': [50.727350349999995, -3.4744726127760086],
                'country_code': 'GB',
                'time_zone': 'Europe/London',
                'Enable GovWifi': 'False',
                'Enable MoJWifi': 'True',
                'Wired NACS Radius Key': 'wired_nacs_secret'
            }
        ]

        self.rf_template_id = "rf_template_123"
        self.network_template_id = "network_template_123"
        self.site_group_ids = '{"moj_wifi": "moj_wifi_id", "gov_wifi": "gov_wifi_id"}'
        self.ap_versions = {"ap_version_1": "1.0", "ap_version_2": "2.0"}

    def test_given_valid_data_when_get_site_payload_called_then_return_built_site_payload(self):
        payload_processor = BuildPayload(
            data=self.sample_data,
            rf_template_id=self.rf_template_id,
            network_template_id=self.network_template_id,
            site_group_ids=self.site_group_ids,
            ap_versions=self.ap_versions
        ).get_site_payload()

        expected_results = [{'site': {'name': 'MOJ-0137-Probation-Gloucestershire-TwyverHouse',
                                      'address': 'Twyver House, Bruton Way, Gloucester, GL1 1PB',
                                      'latlng': {'lat': 51.86467215, 'lng': -2.2396225106929535}, 'country_code': 'GB',
                                      'rftemplate_id': 'rf_template_123', 'networktemplate_id': 'network_template_123',
                                      'timezone': 'Europe/London', 'sitegroup_ids': []}, 'site_setting': {
            'auto_upgrade': {'enabled': True, 'version': 'custom', 'time_of_day': '02:00',
                             'custom_versions': {'ap_version_1': '1.0', 'ap_version_2': '2.0'}, 'day_of_week': ''},
            'rogue': {'min_rssi': -80, 'min_duration': 20, 'enabled': True, 'honeypot_enabled': True,
                      'whitelisted_bssids': [''], 'whitelisted_ssids': ['GovWifi']}, 'persist_config_on_device': True,
            'engagement': {'dwell_tags': {'passerby': '1-300', 'bounce': '3600-14400', 'engaged': '25200-36000',
                                          'stationed': '50400-86400'},
                           'dwell_tag_names': {'passerby': 'Below 5 Min (Passerby)', 'bounce': '1-4 Hours',
                                               'engaged': '7-10 Hours', 'stationed': '14-24 Hours'},
                           'hours': {'sun': None, 'mon': None, 'tue': None, 'wed': None, 'thu': None, 'fri': None,
                                     'sat': None}}, 'analytic': {'enabled': True},
            'rtsa': {'enabled': False, 'track_asset': False, 'app_waking': False},
            'led': {'enabled': True, 'brightness': 255},
            'wifi': {'enabled': True, 'locate_unconnected': True, 'mesh_enabled': False, 'mesh_allow_dfs': False},
            'switch_mgmt': {'use_mxedge_proxy': False, 'mxedge_proxy_port': '2222'}, 'wootcloud': None,
            'skyatp': {'enabled': None, 'send_ip_mac_mapping': None}, 'mgmt': {'use_wxtunnel': False},
            'config_auto_revert': True, 'status_portal': {'enabled': False, 'hostnames': ['']},
            'uplink_port_config': {'keep_wlans_up_if_down': True}, 'ssh_keys': [], 'wids': {},
            'mxtunnel': {'enabled': False},
            'occupancy': {'min_duration': None, 'clients_enabled': False, 'sdkclients_enabled': False,
                          'assets_enabled': False, 'unconnected_clients_enabled': False},
            'public_zone_occupancy': {'enabled': False, 'client_density_enabled': False, 'rssi_zones_enabled': False},
            'zone_occupancy_alert': {'enabled': False, 'threshold': 5, 'email_notifiers': []},
            'gateway_mgmt': {'app_usage': False, 'security_log_source_interface': '',
                             'auto_signature_update': {'enable': True, 'time_of_day': '02:00', 'day_of_week': ''}},
            'tunterm_monitoring': [], 'tunterm_monitoring_disabled': True, 'ssr': {},
            'vars': {'address': 'Twyver House, Bruton Way, Gloucester, GL1 1PB',
                     'site_name': 'MOJ-0137-Probation-Gloucestershire-TwyverHouse',
                     'site_specific_radius_govwifi_secret': 'govwifi_secret',
                     'site_specific_radius_wired_nacs_secret': 'wired_nacs_secret'}}}, {
            'site': {'name': 'Test location 2', 'address': '102 Petty France, London SW1H 9AJ',
                     'latlng': {'lat': 51.499929300000005, 'lng': -0.13477761285315926},
                     'country_code': 'GB', 'rftemplate_id': 'rf_template_123',
                     'networktemplate_id': 'network_template_123', 'timezone': 'Europe/London',
                     'sitegroup_ids': []}, 'site_setting': {
                'auto_upgrade': {'enabled': True, 'version': 'custom', 'time_of_day': '02:00',
                                 'custom_versions': {'ap_version_1': '1.0', 'ap_version_2': '2.0'}, 'day_of_week': ''},
                'rogue': {'min_rssi': -80, 'min_duration': 20, 'enabled': True, 'honeypot_enabled': True,
                          'whitelisted_bssids': [''], 'whitelisted_ssids': []}, 'persist_config_on_device': True,
                'engagement': {'dwell_tags': {'passerby': '1-300', 'bounce': '3600-14400', 'engaged': '25200-36000',
                                              'stationed': '50400-86400'},
                               'dwell_tag_names': {'passerby': 'Below 5 Min (Passerby)', 'bounce': '1-4 Hours',
                                                   'engaged': '7-10 Hours', 'stationed': '14-24 Hours'},
                               'hours': {'sun': None, 'mon': None, 'tue': None, 'wed': None, 'thu': None, 'fri': None,
                                         'sat': None}}, 'analytic': {'enabled': True},
                'rtsa': {'enabled': False, 'track_asset': False, 'app_waking': False},
                'led': {'enabled': True, 'brightness': 255},
                'wifi': {'enabled': True, 'locate_unconnected': True, 'mesh_enabled': False, 'mesh_allow_dfs': False},
                'switch_mgmt': {'use_mxedge_proxy': False, 'mxedge_proxy_port': '2222'}, 'wootcloud': None,
                'skyatp': {'enabled': None, 'send_ip_mac_mapping': None}, 'mgmt': {'use_wxtunnel': False},
                'config_auto_revert': True, 'status_portal': {'enabled': False, 'hostnames': ['']},
                'uplink_port_config': {'keep_wlans_up_if_down': True}, 'ssh_keys': [], 'wids': {},
                'mxtunnel': {'enabled': False},
                'occupancy': {'min_duration': None, 'clients_enabled': False, 'sdkclients_enabled': False,
                              'assets_enabled': False, 'unconnected_clients_enabled': False},
                'public_zone_occupancy': {'enabled': False, 'client_density_enabled': False,
                                          'rssi_zones_enabled': False},
                'zone_occupancy_alert': {'enabled': False, 'threshold': 5, 'email_notifiers': []},
                'gateway_mgmt': {'app_usage': False, 'security_log_source_interface': '',
                                                     'auto_signature_update': {'enable': True, 'time_of_day': '02:00', 'day_of_week': ''}},
                'tunterm_monitoring': [], 'tunterm_monitoring_disabled': True, 'ssr': {},
                'vars': {'address': '102 Petty France, London SW1H 9AJ', 'site_name': 'Test location 2'}}}, {
            'site': {'name': 'Test location 3',
                     'address': 'Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB',
                     'latlng': {'lat': 50.727350349999995, 'lng': -3.4744726127760086},
                     'country_code': 'GB', 'rftemplate_id': 'rf_template_123',
                     'networktemplate_id': 'network_template_123', 'timezone': 'Europe/London',
                     'sitegroup_ids': []}, 'site_setting': {
                'auto_upgrade': {'enabled': True, 'version': 'custom', 'time_of_day': '02:00',
                                 'custom_versions': {'ap_version_1': '1.0', 'ap_version_2': '2.0'}, 'day_of_week': ''},
                'rogue': {'min_rssi': -80, 'min_duration': 20, 'enabled': True, 'honeypot_enabled': True,
                          'whitelisted_bssids': [''], 'whitelisted_ssids': []}, 'persist_config_on_device': True,
                'engagement': {'dwell_tags': {'passerby': '1-300', 'bounce': '3600-14400', 'engaged': '25200-36000',
                                              'stationed': '50400-86400'},
                               'dwell_tag_names': {'passerby': 'Below 5 Min (Passerby)', 'bounce': '1-4 Hours',
                                                   'engaged': '7-10 Hours', 'stationed': '14-24 Hours'},
                               'hours': {'sun': None, 'mon': None, 'tue': None, 'wed': None, 'thu': None, 'fri': None,
                                         'sat': None}}, 'analytic': {'enabled': True},
                'rtsa': {'enabled': False, 'track_asset': False, 'app_waking': False},
                'led': {'enabled': True, 'brightness': 255},
                'wifi': {'enabled': True, 'locate_unconnected': True, 'mesh_enabled': False, 'mesh_allow_dfs': False},
                'switch_mgmt': {'use_mxedge_proxy': False, 'mxedge_proxy_port': '2222'}, 'wootcloud': None,
                'skyatp': {'enabled': None, 'send_ip_mac_mapping': None}, 'mgmt': {'use_wxtunnel': False},
                'config_auto_revert': True, 'status_portal': {'enabled': False, 'hostnames': ['']},
                'uplink_port_config': {'keep_wlans_up_if_down': True}, 'ssh_keys': [], 'wids': {},
                'mxtunnel': {'enabled': False},
                'occupancy': {'min_duration': None, 'clients_enabled': False, 'sdkclients_enabled': False,
                              'assets_enabled': False, 'unconnected_clients_enabled': False},
                'public_zone_occupancy': {'enabled': False, 'client_density_enabled': False,
                                          'rssi_zones_enabled': False},
                'zone_occupancy_alert': {'enabled': False, 'threshold': 5, 'email_notifiers': []},
                'gateway_mgmt': {'app_usage': False, 'security_log_source_interface': '',
                                                     'auto_signature_update': {'enable': True, 'time_of_day': '02:00', 'day_of_week': ''}},
                'tunterm_monitoring': [], 'tunterm_monitoring_disabled': True, 'ssr': {},
                'vars': {'address': 'Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB', 'site_name': 'Test location 3',
                                             'site_specific_radius_wired_nacs_secret': 'wired_nacs_secret'}}}]

        self.assertEqual(payload_processor, expected_results)

    def test_given_invalid_data_when_get_site_payload_called_then_raise_error(self):
        with self.assertRaises(ValueError) as cm:
            BuildPayload(
                data=["I hate bad formatting!"],
                rf_template_id=self.rf_template_id,
                network_template_id=self.network_template_id,
                site_group_ids=self.site_group_ids,
                ap_versions=self.ap_versions
            )

        self.assertEqual(str(cm.exception),
                         "Missing the following keys ['Site Name', 'Site Address', 'gps', 'country_code', 'time_zone', 'Enable GovWifi', 'Enable MoJWifi']")


class TestCheckIfNeedToAppend(unittest.TestCase):

    def setUp(self):
        # Define sample site group IDs for testing
        self.site_group_ids = {
            'moj_wifi': '0b33c61d-8f51-4757-a14d-29263421a904',
            'gov_wifi': '70f3e8af-85c3-484d-8d90-93e28b911efb'
        }
        self.sample_data = [
            {
                'Site Name': 'MOJ-0137-Probation-Gloucestershire-TwyverHouse',
                'Site Address': 'Twyver House, Bruton Way, Gloucester, GL1 1PB',
                'gps': [51.86467215, -2.2396225106929535],
                'country_code': 'GB',
                'time_zone': 'Europe/London',
                'Enable GovWifi': 'True',
                'Enable MoJWifi': 'True',
                'GovWifi Radius Key': 'govwifi_secret',
                'Wired NACS Radius Key': 'wired_nacs_secret'
            },
            {
                'Site Name': 'Test location 2',
                'Site Address': '102 Petty France, London SW1H 9AJ',
                'gps': [51.499929300000005, -0.13477761285315926],
                'country_code': 'GB',
                'time_zone': 'Europe/London',
                'Enable GovWifi': 'False',
                'Enable MoJWifi': 'False'
            },
            {
                'Site Name': 'Test location 3',
                'Site Address': 'Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB',
                'gps': [50.727350349999995, -3.4744726127760086],
                'country_code': 'GB',
                'time_zone': 'Europe/London',
                'Enable GovWifi': 'False',
                'Enable MoJWifi': 'True',
                'Wired NACS Radius Key': 'wired_nacs_secret'
            }
        ]
        self.rf_template_id = "rf_template_123"
        self.network_template_id = "network_template_123"
        self.site_group_ids = {
            "moj_wifi": "moj_wifi_id", "gov_wifi": "gov_wifi_id"}
        self.ap_versions = {"ap_version_1": "1.0", "ap_version_2": "2.0"}
        self.payload_processor = BuildPayload(
            data=self.sample_data,
            rf_template_id=self.rf_template_id,
            network_template_id=self.network_template_id,
            site_group_ids='{"moj_wifi": "moj_wifi_id", "gov_wifi": "gov_wifi_id"}',
            ap_versions=self.ap_versions
        )

    def test_append_gov_wifi(self):
        gov_wifi = 'TRUE'
        moj_wifi = 'FALSE'
        result = self.payload_processor._check_if_we_need_to_append_gov_wifi_or_moj_wifi_site_groups(
            gov_wifi, moj_wifi, self.site_group_ids)
        self.assertEqual(result, [self.site_group_ids['gov_wifi']])

    def test_append_moj_wifi(self):
        gov_wifi = 'FALSE'
        moj_wifi = 'TRUE'
        result = self.payload_processor._check_if_we_need_to_append_gov_wifi_or_moj_wifi_site_groups(
            gov_wifi, moj_wifi, self.site_group_ids)
        self.assertEqual(result, [self.site_group_ids['moj_wifi']])

    def test_append_both_wifi(self):
        gov_wifi = 'TRUE'
        moj_wifi = 'TRUE'
        result = self.payload_processor._check_if_we_need_to_append_gov_wifi_or_moj_wifi_site_groups(
            gov_wifi, moj_wifi, self.site_group_ids)
        expected_result = [self.site_group_ids['moj_wifi'],
                           self.site_group_ids['gov_wifi']]
        self.assertEqual(result, expected_result)

    def test_append_neither_wifi(self):
        gov_wifi = 'FALSE'
        moj_wifi = 'FALSE'
        result = self.payload_processor._check_if_we_need_to_append_gov_wifi_or_moj_wifi_site_groups(
            gov_wifi, moj_wifi, self.site_group_ids)
        self.assertEqual(result, [])
