from juniper import juniper_script
import os
import csv
from geocode import geocode, find_timezone, find_country_code


# Convert CSV file to JSON object.
def convert_csv_to_json(file_path):
    csv_rows = []
    with open(file_path) as csvfile:
        reader = csv.DictReader(csvfile, skipinitialspace=True, quotechar='"')
        title = reader.fieldnames

        for row in reader:
            csv_rows.extend([{title[i]: row[title[i]]
                              for i in range(len(title))}])

    if csv_rows == None or csv_rows == []:
        raise ValueError('Failed to convert CSV file to JSON. Exiting script.')
    return csv_rows


def add_geocoding_to_json(data):
    for d in data:
        # Variables
        site_id = None
        site = {'name': d.get('Site Name', ''),
                'address': d.get('Site Name', '')
                }

        gps = geocode(d.get('Site Address', ''))
        country_code = find_country_code(gps)
        time_zone = find_timezone(gps)

        # Adding new key-value pairs to the dictionary
        d['gps'] = gps
        d['country_code'] = country_code
        d['time_zone'] = time_zone
    return data


if __name__ == '__main__':

    csv_file_path = os.getcwd() + '/../data_src/sites_with_clients.csv'

    # Convert CSV to valid JSON
    json_data_without_geocoding = convert_csv_to_json(csv_file_path)

    json_data_with_geocoding = add_geocoding_to_json(
        json_data_without_geocoding)

    juniper_script(
        mist_api_token=os.environ['MIST_API_TOKEN'],
        org_id=os.environ['ORG_ID'],
        data=json_data_with_geocoding
    )
