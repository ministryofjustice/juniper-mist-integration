import unittest
from unittest.mock import patch, Mock
from src.geocode import geocode

class TestGeocode(unittest.TestCase):

    @patch('src.geocode.Nominatim.geocode')
    def test_given_list_of_valid_addresses_when_geocode_called_then_return_relevant_list_of_gps_locations(self, mock_nominatim):
        # Define a list of addresses and their expected results
        addresses = [
            ("40 Mayflower Dr, Plymouth PL2 3DG", (50.3868633, -4.1539256)),
            ("102 Petty France, London SW1H 9AJ", (51.499929300000005, -0.13477761285315926)),
            ("London", (51.4893335, -0.14405508452768728)),
            ("Met Office, FitzRoy Road, Exeter, Devon, EX1 3PB", (50.727350349999995, -3.4744726127760086))
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

        expected_error_message = 'geocode unable to find latitude & longitude for {address}'.format(address=address)
        self.assertEqual(str(context.exception), expected_error_message)