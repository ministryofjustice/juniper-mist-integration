import unittest
from unittest.mock import patch, MagicMock
from src.geocode import geocode, find_timezone, find_country_code


class TestGeocode(unittest.TestCase):

    @patch('src.geocode.Nominatim.geocode')
    def test_given_list_of_valid_addresses_when_geocode_called_then_return_relevant_list_of_gps_locations(self, mock_nominatim):
        # Define a list of addresses and their expected results
        addresses = [
            ("40 Mayflower Dr, Plymouth PL2 3DG", (50.3868633, -4.1539256)),
            ("102 Petty France, London SW1H 9AJ",
             (51.499929300000005, -0.13477761285315926)),
            ("London", (51.4893335, -0.14405508452768728)),
            ("Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB",
             (50.727350349999995, -3.4744726127760086))
        ]
        # Mock the geocode method to return the corresponding latitude and longitude
        for address, (lat, lon) in addresses:
            mock_nominatim.return_value.latitude = lat
            mock_nominatim.return_value.longitude = lon

            # Call the geocode function for each address
            result = geocode(address)

            # Assert that the result matches the expected latitude and longitude
            self.assertEqual(result, (lat, lon))

    @patch('src.geocode.Nominatim.geocode')
    def test_geocode_invalid_address(self, mock_geocode):
        # Arrange
        address = "Invalid Address"
        mock_geocode.return_value = None  # Simulate geocode returning None

        # Act & Assert
        with self.assertRaises(AttributeError) as context:
            geocode(address)

        expected_error_message = 'geocode unable to find latitude & longitude for {address}'.format(
            address=address)
        self.assertEqual(str(context.exception), expected_error_message)

    @patch('src.geocode.TimezoneFinder')
    def test_find_timezone_valid_coordinates(self, mock_timezone_finder):
        tf_instance = MagicMock()
        tf_instance.timezone_at.return_value = 'America/New_York'
        mock_timezone_finder.return_value = tf_instance

        gps_coordinates = (40.7128, -74.0060)
        result = find_timezone(gps_coordinates)

        self.assertEqual(result, 'America/New_York')

    @patch('src.geocode.TimezoneFinder')
    def test_find_timezone_out_of_bounds(self, mock_timezone_finder):
        tf_instance = MagicMock()
        tf_instance.timezone_at.side_effect = ValueError(
            'The coordinates were out of bounds 40.7128:-74.0060')
        mock_timezone_finder.return_value = tf_instance

        gps_coordinates = (40.7128, -74.0060)

        with self.assertRaises(ValueError) as context:
            find_timezone(gps_coordinates)

        self.assertEqual(str(context.exception),
                         'The coordinates were out of bounds 40.7128:-74.006')

    @patch('src.geocode.TimezoneFinder')
    def test_find_timezone_no_matching_timezone(self, mock_timezone_finder):
        tf_instance = MagicMock()
        tf_instance.timezone_at.return_value = None
        mock_timezone_finder.return_value = tf_instance

        gps_coordinates = (40.7128, -74.0060)

        with self.assertRaises(ValueError) as context:
            find_timezone(gps_coordinates)

        self.assertEqual(str(context.exception),
                         'GPS coordinates did not match a time_zone')


class TestFindCountryCode(unittest.TestCase):
    @patch('src.geocode.Nominatim.geocode')
    def test_find_country_code_valid_coordinates(self, mock_nominatim):
        geolocator_instance = MagicMock()
        location_instance = MagicMock()
        location_instance.raw = {'address': {'country_code': 'us'}}
        geolocator_instance.reverse.return_value = location_instance
        mock_nominatim.return_value = geolocator_instance

        gps_coordinates = (40.7128, -74.0060)
        result = find_country_code(gps_coordinates)

        self.assertEqual(result, 'US')

    @patch('src.geocode.Nominatim.geocode')
    def test_find_country_code_invalid_coordinates(self, mock_nominatim):
        geolocator_instance = MagicMock()
        geolocator_instance.reverse.side_effect = Exception(
            'Invalid coordinates')
        mock_nominatim.return_value = geolocator_instance

        gps_coordinates = (1000.0, 2000.0)  # Invalid coordinates

        with self.assertRaises(Exception) as context:
            find_country_code(gps_coordinates)

        self.assertEqual(str(context.exception),
                         'Must be a coordinate pair or Point')
