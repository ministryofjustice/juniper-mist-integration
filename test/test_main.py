from src.main import convert_csv_to_json
import unittest
import tempfile
import csv

class TestCsvToJson(unittest.TestCase):

    def setUp(self):
        # Create a temporary CSV file for testing
        self.csv_data = [
            {'Site Name': 'Test location 1', 'Site Address': '40 Mayflower Dr, Plymouth PL2 3DG',
             'Enable GovWifi': ' "TRUE"',
             'Enable MoJWifi': ' "FALSE"', 'GovWifi Radius Key': '00000DD0000BC0EEE000',
             'Wired NACS Radius Key': '00000DD0000BC0EEE000'},
            {'Site Name': 'Test location 2', 'Site Address': '102 Petty France, London SW1H 9AJ',
             'Enable GovWifi': ' "TRUE"',
             'Enable MoJWifi': ' "FALSE"', 'GovWifi Radius Key': '0D0E0DDE000BC0EEE000',
             'Wired NACS Radius Key': '00000DD0000BC0EEE000'},
            {'Site Name': 'Test location 3', 'Site Address': 'Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB',
             'Enable GovWifi': ' "TRUE"',
             'Enable MoJWifi': ' "FALSE"', 'GovWifi Radius Key': '0D0E0DDE080BC0EEE000',
             'Wired NACS Radius Key': '00000DD0000BC0EEE000'}
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
        self.csv_writer.writerows(self.csv_data)
        self.csv_file.close()

    def test_convert_csv_to_json_valid_csv(self):
        expected_json = self.csv_data
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

    def test_given_csv_while_when_csv_file_contains_nbsp_then_convert_to_normal_spacing(self):
        csv_data = [
            {'Site\xa0Name': 'Test location 1', 'Site Address': '40\xa0Mayflower\xa0Dr, Plymouth PL2 3DG',
             'Enable GovWifi': ' "TRUE"',
             'Enable\xa0MoJWifi': ' "FALSE"', 'GovWifi\xa0Radius Key': '00000DD0000BC0EEE000',
             'Wired\xa0NACS Radius Key': '00000DD0000BC0EEE000'},
            {'Site\xa0Name': 'Test location 2', 'Site Address': '102\xa0Petty\xa0France, London SW1H 9AJ',
             'Enable GovWifi': ' "TRUE"',
             'Enable\xa0MoJWifi': ' "FALSE"', 'GovWifi\xa0Radius Key': '0D0E0DDE000BC0EEE000',
             'Wired\xa0NACS Radius Key': '00000DD0000BC0EEE000'},
            {'Site\xa0Name': 'Test location 3', 'Site Address': 'Met\xa0Office, FitzRoy Road,\xa0Exeter, Devon, EX1 3PB',
             'Enable GovWifi': ' "TRUE"',
             'Enable\xa0MoJWifi': ' "FALSE"', 'GovWifi\xa0Radius Key': '0D0E0DDE080BC0EEE000',
             'Wired\xa0NACS Radius Key': '00000DD0000BC0EEE000'}
        ]
        csv_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, newline='', suffix='.csv')
        csv_writer = csv.DictWriter(csv_file, fieldnames=[
            'Site\xa0Name',
            'Site Address',
            'Enable GovWifi',
            'Enable\xa0MoJWifi',
            'GovWifi\xa0Radius Key',
            'Wired\xa0NACS Radius Key'
        ])
        csv_writer.writeheader()
        csv_writer.writerows(csv_data)
        csv_file.close()

        expected_json = self.csv_data
        actual_json = convert_csv_to_json(csv_file.name)
        self.assertEqual(actual_json, expected_json)
