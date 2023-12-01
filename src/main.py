from juniper import juniper_script
import os, csv
from geocode import geocode, find_timezone, find_country_code


# Convert CSV file to JSON object.
def csv_to_json(file_path):
    csv_rows = []
    with open(file_path) as csvfile:
        reader = csv.DictReader(csvfile, skipinitialspace=True, quotechar='"')
        title = reader.fieldnames

        for row in reader:
            csv_rows.extend([ {title[i]: row[title[i]] for i in range(len(title))} ])

    return csv_rows

if __name__ == '__main__':

    csv_file_path=os.getcwd() + '/../test_data/sites_with_clients.csv'

    # Convert CSV to valid JSON
    data = csv_to_json(csv_file_path)
    if data == None or data == []:
        raise ValueError('Failed to convert CSV file to JSON. Exiting script.')


    # Create each site from the CSV file
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

    juniper_script(
        mist_api_token=os.environ['MIST_API_TOKEN'],
        org_id=os.environ['ORG_ID'],
        data=data
    )
