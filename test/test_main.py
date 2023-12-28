import unittest
import tempfile
import csv
from unittest.mock import patch
from src.main import convert_csv_to_json, add_geocoding_to_json, clean_csv_rows_by_removing_nbsp


class TestCsvToJson(unittest.TestCase):

    def setUp(self):
        # Create a temporary CSV file for testing
        self.csv_data = [
            {'Site Name': 'Test location 1', 'Site Address': '40 Mayflower Dr, Plymouth PL2 3DG', 'Enable GovWifi': ' "TRUE"',
                'Enable MoJWifi': ' "FALSE"', 'GovWifi Radius Key': '00000DD0000BC0EEE000', 'Wired NACS Radius Key': '00000DD0000BC0EEE000'},
            {'Site Name': 'Test location 2', 'Site Address': '102 Petty France, London SW1H 9AJ', 'Enable GovWifi': ' "TRUE"',
                'Enable MoJWifi': ' "FALSE"', 'GovWifi Radius Key': '0D0E0DDE000BC0EEE000', 'Wired NACS Radius Key': '00000DD0000BC0EEE000'},
            {'Site Name': 'Test location 3', 'Site Address': 'Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB', 'Enable GovWifi': ' "TRUE"',
                'Enable MoJWifi': ' "FALSE"', 'GovWifi Radius Key': '0D0E0DDE080BC0EEE000', 'Wired NACS Radius Key': '00000DD0000BC0EEE000'},
            {'Site Name': 'non\xa0breaking\xa0space\xa0test', 'Site Address': 'Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB', 'Enable GovWifi': ' "TRUE"',
             'Enable MoJWifi': ' "FALSE"', 'GovWifi Radius Key': '0D0E0DDE080BC0EEE000', 'Wired NACS Radius Key': '00000DD0000BC0EEE000'}
        ]
        self.csv_data_expected = [
            {'Site Name': 'Test location 1', 'Site Address': '40 Mayflower Dr, Plymouth PL2 3DG', 'Enable GovWifi': ' "TRUE"',
             'Enable MoJWifi': ' "FALSE"', 'GovWifi Radius Key': '00000DD0000BC0EEE000', 'Wired NACS Radius Key': '00000DD0000BC0EEE000'},
            {'Site Name': 'Test location 2', 'Site Address': '102 Petty France, London SW1H 9AJ', 'Enable GovWifi': ' "TRUE"',
             'Enable MoJWifi': ' "FALSE"', 'GovWifi Radius Key': '0D0E0DDE000BC0EEE000', 'Wired NACS Radius Key': '00000DD0000BC0EEE000'},
            {'Site Name': 'Test location 3', 'Site Address': 'Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB', 'Enable GovWifi': ' "TRUE"',
             'Enable MoJWifi': ' "FALSE"', 'GovWifi Radius Key': '0D0E0DDE080BC0EEE000', 'Wired NACS Radius Key': '00000DD0000BC0EEE000'},
            {'Site Name': 'non breaking space test', 'Site Address': 'Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB', 'Enable GovWifi': ' "TRUE"',
             'Enable MoJWifi': ' "FALSE"', 'GovWifi Radius Key': '0D0E0DDE080BC0EEE000', 'Wired NACS Radius Key': '00000DD0000BC0EEE000'}
        ]
        self.csv_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, newline='', suffix='.csv')
        self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=[
            'Site Name',
            'Site Address',
            'Enable GovWifi',
            'Enable MoJWifi',
            'GovWifi Radius Key',
            'Wired NACS Radius Key'
        ])
        self.csv_writer.writeheader()
        self.csv_writer.writerows(self.csv_data_expected)
        self.csv_file.close()

    def test_convert_csv_to_json_valid_csv(self):
        expected_json = self.csv_data_expected
        actual_json = convert_csv_to_json(self.csv_file.name)
        self.assertEqual(actual_json, expected_json)

    def test_given_csv_file_when_csv_file_empty_then_raise_value_error(self):
        empty_csv_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, newline='', suffix='.csv')
        empty_csv_file.close()
        with self.assertRaises(ValueError) as error:
            convert_csv_to_json(empty_csv_file.name)
        self.assertEqual(str(error.exception),
                         'Failed to convert CSV file to JSON. Exiting script.')

    def test_given_file_path_when_csv_file_not_found_then_raise_FileNotFoundError(self):
        # Test if the function handles a nonexistent CSV file correctly
        nonexistent_file_path = 'nonexistent.csv'
        with self.assertRaises(FileNotFoundError):
            convert_csv_to_json(nonexistent_file_path)


class TestAddGeocodingToJson(unittest.TestCase):

    @patch('src.main.geocode', side_effect=[
        {'latitude': 50.3868633, 'longitude': -4.1539256},
        {'latitude': 51.499929300000005, 'longitude': -0.13477761285315926},
        {'latitude': 50.727350349999995, 'longitude': -3.4744726127760086},
    ])
    @patch('src.main.find_country_code', return_value='GB')
    @patch('src.main.find_timezone', return_value='Europe/London')
    def test_given_site_name_and_site_address_in_json_format_when_function_called_then_add_geocode_country_code_and_time_zone(
            self,
            find_timezone,
            mock_find_country_code,
            mock_geocode
    ):
        # Test if the function adds geocoding information correctly
        data = [
            {'Site Name': 'Site1', 'Site Address': '40 Mayflower Dr, Plymouth PL2 3DG'},
            {'Site Name': 'Site2', 'Site Address': '102 Petty France, London SW1H 9AJ'},
            {'Site Name': 'Site3',
                'Site Address': 'Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB'}
        ]

        expected_data = [
            {'Site Name': 'Site1', 'Site Address': '40 Mayflower Dr, Plymouth PL2 3DG', 'gps': {
                'latitude': 50.3868633, 'longitude': -4.1539256}, 'country_code': 'GB', 'time_zone': 'Europe/London'},
            {'Site Name': 'Site2', 'Site Address': '102 Petty France, London SW1H 9AJ', 'gps': {
                'latitude': 51.499929300000005, 'longitude': -0.13477761285315926}, 'country_code': 'GB', 'time_zone': 'Europe/London'},
            {'Site Name': 'Site3', 'Site Address': 'Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB', 'gps': {
                'latitude': 50.727350349999995, 'longitude': -3.4744726127760086}, 'country_code': 'GB', 'time_zone': 'Europe/London'}
        ]

        actual_data = add_geocoding_to_json(data)

        self.assertEqual(actual_data, expected_data)
        find_timezone.assert_called()
        mock_find_country_code.assert_called()
        mock_geocode.assert_called()


class TestCleanCSVRows(unittest.TestCase):

    def test_clean_csv_rows_no_nbsp(self):
        input_data = [
            {'Site Name': 'Test location 1', 'Site Address': '40 Mayflower Dr, Plymouth PL2 3DG', 'Enable GovWifi': ' "TRUE"',
             'Enable MoJWifi': ' "FALSE"', 'GovWifi Radius Key': '00000DD0000BC0EEE000', 'Wired NACS Radius Key': '00000DD0000BC0EEE000'},
            {'Site Name': 'Test location 2', 'Site Address': '102 Petty France, London SW1H 9AJ', 'Enable GovWifi': ' "TRUE"',
             'Enable MoJWifi': ' "FALSE"', 'GovWifi Radius Key': '0D0E0DDE000BC0EEE000', 'Wired NACS Radius Key': '00000DD0000BC0EEE000'}
        ]
        output_data = clean_csv_rows_by_removing_nbsp(input_data)
        self.assertEqual(output_data, input_data, "No non-breaking spaces, should be unchanged")

    def test_keys_clean_csv_rows_with_nbsp(self):
        input_data = [
            {'Site\xa0Name': 'non breaking space test', 'Site Address': 'Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB', 'Enable GovWifi': ' "TRUE"',
             'Enable MoJWifi': ' "FALSE"', 'GovWifi Radius Key': '0D0E0DDE080BC0EEE000', 'Wired NACS Radius Key': '00000DD0000BC0EEE000'},
            {'Site Name': 'non breaking space test', 'Site Address': 'Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB', 'Enable GovWifi': ' "TRUE"',
             'Enable MoJWifi': ' "FALSE"', 'GovWifi Radius Key': '0D0E0DDE080BC0EEE000', 'Wired NACS Radius Key': '00000DD0000BC0EEE000'}
        ]
        expected_output = [{'Enable GovWifi': ' "TRUE"',
                            'Enable MoJWifi': ' "FALSE"',
                            'GovWifi Radius Key': '0D0E0DDE080BC0EEE000',
                            'Site Address': 'Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB',
                            'Site Name': 'non breaking space test',
                            'Wired NACS Radius Key': '00000DD0000BC0EEE000'},
                           {'Enable GovWifi': ' "TRUE"',
                            'Enable MoJWifi': ' "FALSE"',
                            'GovWifi Radius Key': '0D0E0DDE080BC0EEE000',
                            'Site Address': 'Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB',
                            'Site Name': 'non breaking space test',
                            'Wired NACS Radius Key': '00000DD0000BC0EEE000'}]
        output_data = clean_csv_rows_by_removing_nbsp(input_data)
        self.assertEqual(output_data, expected_output, "Non-breaking spaces should be removed")

    def test_values_clean_csv_rows_with_nbsp(self):
        input_data = [
            {'Site Name': 'non\xa0breaking\xa0space\xa0test', 'Site Address': 'Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB', 'Enable GovWifi': ' "TRUE"',
             'Enable MoJWifi': ' "FALSE"', 'GovWifi Radius Key': '0D0E0DDE080BC0EEE000', 'Wired NACS Radius Key': '00000DD0000BC0EEE000'},
            {'Site Name': 'non breaking\xa0space test', 'Site Address': 'Met Office, FitzRoy Road, Exeter, Devon, EX1\xa03PB', 'Enable GovWifi': ' "TRUE"',
             'Enable MoJWifi': ' "FALSE"', 'GovWifi Radius Key': '0D0E0DDE080BC0EEE000', 'Wired NACS Radius Key': '00000DD0000BC0EEE000'}
        ]
        expected_output = [{'Enable GovWifi': ' "TRUE"',
                            'Enable MoJWifi': ' "FALSE"',
                            'GovWifi Radius Key': '0D0E0DDE080BC0EEE000',
                            'Site Address': 'Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB',
                            'Site Name': 'non breaking space test',
                            'Wired NACS Radius Key': '00000DD0000BC0EEE000'},
                           {'Enable GovWifi': ' "TRUE"',
                            'Enable MoJWifi': ' "FALSE"',
                            'GovWifi Radius Key': '0D0E0DDE080BC0EEE000',
                            'Site Address': 'Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB',
                            'Site Name': 'non breaking space test',
                            'Wired NACS Radius Key': '00000DD0000BC0EEE000'}]
        output_data = clean_csv_rows_by_removing_nbsp(input_data)
        self.assertEqual(output_data, expected_output, "Non-breaking spaces should be removed")

    def test_keys_and_values_clean_csv_rows_with_nbsp(self):
        input_data = [
            {'Site\xa0Name': 'non breaking\xa0space\xa0test', 'Site Address': 'Met Office, FitzRoy\xa0Road, Exeter, Devon, EX1 3PB', 'Enable GovWifi': ' "TRUE"',
             'Enable MoJWifi': ' "FALSE"', 'GovWifi Radius Key': '0D0E0DDE080BC0EEE000', 'Wired\xa0NACS Radius Key': '00000DD0000BC0EEE000'},
            {'Site Name': 'non breaking space test', 'Site Address': 'Met Office, FitzRoy Road, Exeter, Devon, EX1\xa03PB', 'Enable GovWifi': ' "TRUE"',
             'Enable MoJWifi': ' "FALSE"', 'GovWifi Radius Key': '0D0E0DDE080BC0EEE000', 'Wired NACS Radius Key': '00000DD0000BC0EEE000'}
        ]
        expected_output = [{'Enable GovWifi': ' "TRUE"',
                            'Enable MoJWifi': ' "FALSE"',
                            'GovWifi Radius Key': '0D0E0DDE080BC0EEE000',
                            'Site Address': 'Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB',
                            'Site Name': 'non breaking space test',
                            'Wired NACS Radius Key': '00000DD0000BC0EEE000'},
                           {'Enable GovWifi': ' "TRUE"',
                            'Enable MoJWifi': ' "FALSE"',
                            'GovWifi Radius Key': '0D0E0DDE080BC0EEE000',
                            'Site Address': 'Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB',
                            'Site Name': 'non breaking space test',
                            'Wired NACS Radius Key': '00000DD0000BC0EEE000'}]
        output_data = clean_csv_rows_by_removing_nbsp(input_data)
        self.assertEqual(output_data, expected_output, "Non-breaking spaces should be removed")
