import unittest


def validate_if_site_defined_on_csv_exists_in_mist(mist_sites_configs: list['dict'],
                                                   ap_csv: list['dict']):
    mist_site_names = []
    for mist_site_config in mist_sites_configs:
        mist_site_names.append(mist_site_config['name'])

    mist_site_names_csv_file = []
    for ap_row in ap_csv:
        mist_site_names_csv_file.append(ap_row['Site Name'])

    for site_name in mist_site_names_csv_file:
        if site_name not in mist_site_names:
            raise ValueError(
                f"Site name '{site_name}' found in CSV file but not in mist site configurations.")


class TestValidateIfSiteDefinedOnCSVExistsInMist(unittest.TestCase):

    def test_all_sites_exist(self):
        mist_sites_configs = [{'name': 'SiteA'},
                              {'name': 'SiteB'}, {'name': 'SiteC'}]
        ap_csv = [{'Site Name': 'SiteA'}, {
            'Site Name': 'SiteB'}, {'Site Name': 'SiteC'}]
        try:
            validate_if_site_defined_on_csv_exists_in_mist(
                mist_sites_configs, ap_csv)
        except ValueError:
            self.fail(
                "validate_if_site_defined_on_csv_exists_in_mist() raised ValueError unexpectedly!")

    def test_site_not_exist(self):
        mist_sites_configs = [{'name': 'SiteA'},
                              {'name': 'SiteB'}, {'name': 'SiteC'}]
        ap_csv = [{'Site Name': 'SiteA'}, {'Site Name': 'SiteD'}]
        with self.assertRaises(ValueError) as cm:
            validate_if_site_defined_on_csv_exists_in_mist(
                mist_sites_configs, ap_csv)
        self.assertEqual(str(
            cm.exception), "Site name 'SiteD' found in CSV file but not in mist site configurations.")

    def test_empty_mist_sites_configs(self):
        mist_sites_configs = []
        ap_csv = [{'Site Name': 'SiteA'}, {'Site Name': 'SiteB'}]
        with self.assertRaises(ValueError) as cm:
            validate_if_site_defined_on_csv_exists_in_mist(
                mist_sites_configs, ap_csv)
        self.assertEqual(str(
            cm.exception), "Site name 'SiteA' found in CSV file but not in mist site configurations.")

    def test_empty_ap_csv(self):
        mist_sites_configs = [{'name': 'SiteA'}, {'name': 'SiteB'}]
        ap_csv = []
        try:
            validate_if_site_defined_on_csv_exists_in_mist(
                mist_sites_configs, ap_csv)
        except ValueError:
            self.fail(
                "validate_if_site_defined_on_csv_exists_in_mist() raised ValueError unexpectedly!")

    def test_both_lists_empty(self):
        mist_sites_configs = []
        ap_csv = []
        try:
            validate_if_site_defined_on_csv_exists_in_mist(
                mist_sites_configs, ap_csv)
        except ValueError:
            self.fail(
                "validate_if_site_defined_on_csv_exists_in_mist() raised ValueError unexpectedly!")


def validate_if_ap_defined_on_csv_exists_in_mist(mist_inventory, ap_csv):
    ap_mac_addresses_from_mist = []
    for inventory_item in mist_inventory:
        if inventory_item['type'] == 'ap':
            ap_mac_addresses_from_mist.append(inventory_item['mac'])

    ap_mac_addresses_from_csv = []
    for ap_row in ap_csv:
        cleaned_mac_address = ap_row['MAC Address'].replace(":", "")
        ap_mac_addresses_from_csv.append(cleaned_mac_address)

    for site_name in ap_mac_addresses_from_csv:
        if site_name not in ap_mac_addresses_from_mist:
            raise ValueError(
                f"Site name '{site_name}' found in CSV file but not in mist site configurations.")


class TestValidateAP(unittest.TestCase):

    def test_all_aps_exist(self):
        mist_inventory = [{'type': 'ap', 'mac': 'aabbccddeeff'}, {
            'type': 'ap', 'mac': '112233445566'}]
        ap_csv = [{'MAC Address': 'aa:bb:cc:dd:ee:ff'},
                  {'MAC Address': '11:22:33:44:55:66'}]
        try:
            validate_if_ap_defined_on_csv_exists_in_mist(
                mist_inventory, ap_csv)
        except ValueError:
            self.fail(
                "validate_if_ap_defined_on_csv_exists_in_mist raised ValueError unexpectedly!")

    def test_missing_ap_in_mist(self):
        mist_inventory = [{'type': 'ap', 'mac': 'aabbccddeeff'}]
        ap_csv = [{'MAC Address': 'aa:bb:cc:dd:ee:ff'},
                  {'MAC Address': '11:22:33:44:55:66'}]
        with self.assertRaises(ValueError) as context:
            validate_if_ap_defined_on_csv_exists_in_mist(
                mist_inventory, ap_csv)
        self.assertIn("Site name '112233445566' found in CSV file but not in mist site configurations.",
                      str(context.exception))

    def test_empty_csv(self):
        mist_inventory = [{'type': 'ap', 'mac': 'aabbccddeeff'}, {
            'type': 'ap', 'mac': '112233445566'}]
        ap_csv = []
        try:
            validate_if_ap_defined_on_csv_exists_in_mist(
                mist_inventory, ap_csv)
        except ValueError:
            self.fail(
                "validate_if_ap_defined_on_csv_exists_in_mist raised ValueError unexpectedly!")

    def test_mixed_inventory(self):
        mist_inventory = [{'type': 'ap', 'mac': 'aabbccddeeff'}, {
            'type': 'switch', 'mac': '112233445566'}]
        ap_csv = [{'MAC Address': 'aa:bb:cc:dd:ee:ff'}]
        try:
            validate_if_ap_defined_on_csv_exists_in_mist(
                mist_inventory, ap_csv)
        except ValueError:
            self.fail(
                "validate_if_ap_defined_on_csv_exists_in_mist raised ValueError unexpectedly!")


if __name__ == '__main__':
    unittest.main()
