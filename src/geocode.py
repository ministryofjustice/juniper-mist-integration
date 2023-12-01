from geopy import Nominatim
from timezonefinder import TimezoneFinder


def geocode(address) -> str:
    geolocator = Nominatim(user_agent="geocode")
    location = geolocator.geocode(address)
    try:
        latitude, longitude = location.latitude, location.longitude
    except AttributeError as e:
        if "'NoneType' object has no attribute 'latitude'" in str(e):
            raise AttributeError(
                'geocode unable to find latitude & longitude for {address}'.format(address=address))
        if "'NoneType' object has no attribute 'longitude'" in str(e):
            raise AttributeError(
                'geocode unable to find latitude & longitude for {address}'.format(address=address))
        else:
            raise  # Re-raise the original AttributeError if the message doesn't match
    return latitude, longitude


def find_country_code(gps) -> tuple:
    latitude = gps[0]
    longitude = gps[1]
    geolocator = Nominatim(user_agent="geocode")
    location = geolocator.reverse([latitude, longitude])
    country_code = location.raw['address']['country_code']

    return country_code.upper()


def find_timezone(gps) -> tuple:
    tf_init = TimezoneFinder()
    latitude = gps[0]
    longitude = gps[1]
    try:
        timezone_name = tf_init.timezone_at(lat=latitude, lng=longitude)
    except ValueError:
        raise ValueError('The coordinates were out of bounds {latitude}:{longitude}'.format(
            lat=latitude, lng=longitude))
    if timezone_name is None:
        raise ValueError('GPS coordinates did not match a time_zone')

    return timezone_name
