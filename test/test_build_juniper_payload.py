from src.build_juniper_payload import BuildPayload
import unittest

class TestBuildPayLoad(unittest.TestCase):
    def setUp(self):
        self.inputt = [
            {
              'Site Name': 'MOJ-0137-Probation-Gloucestershire-TwyverHouse',
              'Site Address': 'Twyver House, Bruton Way, Gloucester, GL1 1PB',
              'Enable GovWifi': 'FALSE', 'Enable MoJWifi': 'FALSE',
              'Wired NACS Radius Key': 'B49DA885C90D8977F984',
              'gps': (51.86467215, -2.2396225106929535),
              'country_code': 'GB', 'time_zone': 'Europe/London'
            },
            {
              'Site Name': 'Test location 2',
              'Site Address': '102 Petty France, London SW1H 9AJ',
              'Enable GovWifi': 'FALSE', 'Enable MoJWifi': 'FALSE',
              'Wired NACS Radius Key': '00000DD0000BC0EEE000',
              'gps': (51.499929300000005, -0.13477761285315926),
              'country_code': 'GB', 'time_zone': 'Europe/London'
            },
            {
              'Site Name': 'Test location 3',
              'Site Address': 'Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB',
              'Enable GovWifi': 'FALSE', 'Enable MoJWifi': 'FALSE',
              'Wired NACS Radius Key': '00000DD0000BC0EEE000', 'gps': (50.727350349999995, -3.4744726127760086),
              'country_code': 'GB', 'time_zone': 'Europe/London'
            }
        ]
        self.payload_processor = BuildPayload(
                data = self.inputt,
                rf_template_id = "rf_template_id",
                network_template_id = "network_template_id",
                site_group_ids = {"moj_wifi": "foo","gov_wifi": "bar"},
                ap_versions = {"AP45": "0.12.27139", "AP32": "0.12.27139"}
            )

    def test_something(self):
        # result = self.payload_processor.get_site_payload()
        print(self.input)

        # self.assertEqual(result[0], {'address': '123 Main St',
        #                              'country_code': 'US',
        #                              'latlng': {'lat': 1.23,'lng': 4.56},
        #                              'name': 'TestSite',
        #                              'networktemplate_id': ('network_template_id',),
        #                              'rftemplate_id': ('rf_template_id',),
        #                              'sitegroup_ids': [],
        #                              'timezone': 'UTC'})
