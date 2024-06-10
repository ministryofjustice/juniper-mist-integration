from juniper_site_creation import juniper_script_site_creation
from juniper_ap_staging import juniper_ap_assign
import os
import csv_utils

if __name__ == '__main__':

    csv_file_path = os.getcwd() + '/../data_src/' + os.environ.get('CSV_FILE_NAME')

    json_data = csv_utils.convert_csv_to_json(csv_file_path)

    operation = os.environ.get('OPERATION')

    if operation is None:
        raise EnvironmentError(
            "The OPERATION environment variable is not set.")

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
