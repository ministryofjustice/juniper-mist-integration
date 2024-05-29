from juniper_site_creation import juniper_script_site_creation
from juniper_ap_staging import juniper_ap_assign
import os
import csv


# Convert CSV file to JSON object.
def convert_csv_to_json(file_path):
    csv_rows = []
    with open(file_path) as csvfile:
        reader = csv.DictReader(csvfile, skipinitialspace=True, quotechar='"')

        # Here we clean any Non-breaking spaces and convert to normal spacing. \xa0 converts to ' '
        for row in reader:
            temp_overwritable_dict = {}
            for key, value in row.items():
                cleaned_key = key.replace('\xa0', ' ')
                cleaned_value = value.replace('\xa0', ' ')
                temp_overwritable_dict.update({cleaned_key: cleaned_value})
            csv_rows.append(temp_overwritable_dict)

    if csv_rows == None or csv_rows == []:
        raise ValueError('Failed to convert CSV file to JSON. Exiting script.')
    return csv_rows


if __name__ == '__main__':

    csv_file_path = os.getcwd() + '/../data_src/' + os.environ.get('CSV_FILE_NAME')

    # Convert CSV to valid JSON
    json_data = convert_csv_to_json(csv_file_path)

    operation = os.environ.get('OPERATION')

    if operation is None:
        raise EnvironmentError("The OPERATION environment variable is not set.")

    if operation == "site_creation":
        juniper_script_site_creation(
            mist_username=os.environ.get('MIST_USERNAME'),
            mist_login_method=os.environ.get('MIST_LOGIN_METHOD'),
            site_group_ids=os.environ.get('SITE_GROUP_IDS'),
            org_id=os.environ.get('ORG_ID'),
            rf_template_id=os.environ.get('RF_TEMPLATE_ID'),
            json_data_without_geocoding=json_data,
            network_template_id=os.environ.get('NETWORK_TEMPLATE_ID'),
            ap_versions=os.environ.get('AP_VERSIONS')
        )
    elif operation == "ap_staging":
        juniper_ap_assign(
            ap_csv=json_data,
            mist_username=os.environ.get('MIST_USERNAME'),
            mist_login_method=os.environ.get('MIST_LOGIN_METHOD'),
            org_id=os.environ.get('ORG_ID')
        )
    else:
        raise ValueError(f"The OPERATION '{operation}' is not recognized.")


