import requests
import json
import getpass
import sys
from datetime import datetime
from build_juniper_payload import BuildPayload

# Mist CRUD operations


class Admin:

    def login_via_username_and_password(self, username):
        # If no username defined ask user
        if username is None:
            username = input("Enter Mist Username:")
        else:
            print('Username provided: {usr}'.format(usr=username))
        password = getpass.getpass(prompt='Enter Mist password:')
        login_url = self.base_url + "/login"
        login_payload = {'email': username, 'password': password}
        self.session.post(login_url, data=login_payload)
        mfa_headers = {
            # Include CSRF token in headers
            'X-CSRFToken': self.session.cookies.get('csrftoken.eu'),
        }
        self.session.headers.update(mfa_headers)
        mfa_code = input("Enter MFA:")
        login_response = self.session.post(
            "https://api.eu.mist.com/api/v1/login/two_factor",
            data={"two_factor": mfa_code}
        )
        if login_response.status_code == 200:
            print("Login successful")
        else:
            raise ValueError("Login was not successful: {response}".format(
                response=login_response))

    def login_via_token(self):
        token = getpass.getpass(prompt='Input the MIST API TOKEN:')
        self.headers['Authorization'] = 'Token ' + token
        request_url = self.base_url + "/self/apitokens"
        responce = self.session.get(request_url, headers=self.headers)
        if responce.status_code == 200:
            print("Login successful")
        else:
            raise ValueError(
                "Login was not successful via token: {response}".format(response=responce))

    def __init__(self, username=None, mist_login_method=None):
        self.session = requests.Session()
        self.headers = {'Content-Type': 'application/json'}
        self.base_url = 'https://api.eu.mist.com/api/v1'

        if mist_login_method == 'token':
            self.login_via_token()
        elif mist_login_method == 'credentials':
            self.login_via_username_and_password(username)
        else:
            raise ValueError('Invalid mist_login_method: {method}'.format(
                method=mist_login_method))

    def post(self, url, payload, timeout=60):
        url = 'https://api.eu.mist.com{}'.format(url)
        session = self.session
        headers = self.headers

        print('POST {}'.format(url))
        response = session.post(url, headers=headers, json=payload)

        if response.status_code != 200:
            print('Failed to POST')
            print('\tURL: {}'.format(url))
            print('\tPayload: {}'.format(payload))
            print('\tResponse: {} ({})'.format(
                response.text, response.status_code))
            return False

        return json.loads(response.text)

    def put(self, url, payload):
        url = 'https://api.eu.mist.com{}'.format(url)
        session = self.session
        headers = self.headers

        print('PUT {}'.format(url))
        response = session.put(url, headers=headers, json=payload)

        if response.status_code != 200:
            print('Failed to PUT')
            print('\tURL: {}'.format(url))
            print('\tPayload: {}'.format(payload))
            print('\tResponse: {} ({})'.format(
                response.text, response.status_code))
            return False

        return json.loads(response.text)


def warn_if_using_org_id_production(org_id):
    production_org_ids = [
        '3e824dd6-6b37-4cc7-90bb-97d744e91175',
        '9fd50080-520d-49ec-96a0-09f263fc8a05'
                          ]
    for production_org_id in production_org_ids:
        if org_id == production_org_id:
            production_warning_answer = input(
                "Warning you are using production ORG_ID, would you like to proceed? Y/N: ").upper()
            if production_warning_answer == "Y":
                print("Continuing with run")
                return 'Continuing_with_run'
            elif production_warning_answer == "N":
                sys.exit()
            else:
                raise ValueError('Invalid input')


def plan_of_action(
        payload_processor
):

    # Generate a timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plan_file_name = "../data_src/mist_plan_{time}.json".format(time=timestamp)

    processed_payload = payload_processor.get_site_payload()

    # Load file
    with open(plan_file_name, "w") as plan_file:
        json.dump(processed_payload, plan_file, indent=2)

    # Print to terminal
    with open(plan_file_name, "r") as plan_file:
        print(plan_file.read())

    print("A file containing all the changes has been created: {file}".format(
        file=plan_file_name))
    user_input = input("Do you wish to continue? (y/n): ").upper()

    if user_input == "Y":
        print("Continuing with run")
    elif user_input == "N":
        sys.exit(0)
    else:
        raise ValueError('Invalid input')


def validate_user_defined_config_variables(
        org_id,
        site_group_ids,
        rf_template_id,
        network_template_id,
        mist_login_method,
        ap_versions
):
    # Check for required variables
    if org_id is None or org_id == '':
        raise ValueError('Please provide Mist org_id')
    if site_group_ids is None:
        raise ValueError('Must provide site_group_ids for GovWifi & MoJWifi')
    if rf_template_id is None:
        raise ValueError('Must define rf_template_id')
    if network_template_id is None:
        raise ValueError('Must define network_template_id')
    if mist_login_method is None:
        print("mist_login_method not defined. Defaulting to credentials")
        mist_login_method = 'credentials'
    if ap_versions is None:  # or not isinstance(ap_versions, dict):
        raise ValueError('Must provide a valid dictionary for ap_versions')

# Main function


def juniper_script(
        data,
        org_id=None,
        mist_username=None,
        mist_login_method=None,
        site_group_ids=None,
        rf_template_id=None,
        network_template_id=None,
        ap_versions=None
):
    # Configure True/False to enable/disable additional logging of the API response objects
    show_more_details = True

    validate_user_defined_config_variables(
        org_id,
        site_group_ids,
        rf_template_id,
        network_template_id,
        mist_login_method,
        ap_versions
    )

    # Prompt user if we are using production org_id
    warn_if_using_org_id_production(org_id)

    payload_processor = BuildPayload(data,
                                     rf_template_id,
                                     network_template_id,
                                     site_group_ids,
                                     ap_versions
                                     )

    plan_of_action(
        payload_processor
    )

    # Establish Mist session
    admin = Admin(mist_username, mist_login_method)


    #TODO get json objects from state here and loop them to upload to mist


    # Create each site from the CSV file
    for site_with_site_setting in payload_processor.get_site_payload():
        # Variables
        site_id = None
        # print(site_with_site_setting)


        print('Calling the Mist Create Site API...')
        result = admin.post('/api/v1/orgs/' + org_id + '/sites', site_with_site_setting["site"])
        if result == False:
            print('Failed to create site {}'.format(site_with_site_setting["site"]['name']))
            print('Skipping remaining operations for this site...')
            print('\n\n==========\n\n')

            continue
        else:
            site_id = result['id']
            print('Created site {} ({})'.format(site_with_site_setting["site"]['name'], site_id))

            if show_more_details:
                print('\nRetrieving the JSON response object...')
                print(json.dumps(result, sort_keys=True, indent=4))
                print('\nUsing id in the Mist Update Setting API request')

        # Update Site Setting
        print('Calling the Mist Update Setting API...')
        result = admin.put('/api/v1/sites/' + site_id + '/setting',
                           site_with_site_setting["site_setting"])
        if result == False:
            print('Failed to update site setting {} ({})'.format(
                site_with_site_setting["site"]['name'], site_id))
        else:
            print('Updated site setting {} ({})'.format(site_with_site_setting["site"]['name'], site_id))

            if show_more_details:
                print('\nRetrieving the JSON response object...')
                print(json.dumps(result, sort_keys=True, indent=4))

        print('\n\n==========\n\n')
