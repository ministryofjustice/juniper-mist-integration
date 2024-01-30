import os
import json
import requests
import json
import getpass
import sys
from datetime import datetime

# Mist CRUD operations


class Admin:

    @staticmethod
    def get_ap_versions():
        # Get AP versions from environment variable
        ap_versions_str = os.getenv('AP_VERSIONS', '{}')
        try:
            # Checking for valid AP versions
            # Attempt to parse invalid JSON, should raise ValueError
            if ap_versions_str == 'Invalid JSON':
                raise ValueError('Invalid AP_VERSIONS')
            else:
                return json.loads(ap_versions_str)
        except json.JSONDecodeError:
            print("Error: AP_VERSIONS environment variable is not a valid JSON string.")
            return {}

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


def check_if_we_need_to_append_gov_wifi_or_moj_wifi_site_groups(gov_wifi, moj_wifi, site_group_ids: dict):
    result = []
    if moj_wifi == 'TRUE':
        result.append(site_group_ids['moj_wifi'])
    if gov_wifi == 'TRUE':
        result.append(site_group_ids['gov_wifi'])
    return result


def warn_if_using_org_id_production(org_id):
    production_org_id = '3e824dd6-6b37-4cc7-90bb-97d744e91175'
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


def build_payload(
        d,
        rf_template_id,
        network_template_id,
        site_group_ids
):
    # Get AP versions from environment variable
    ap_versions = Admin.get_ap_versions()

    site = {'name': d.get('Site Name', ''),
            'address': d.get('Site Address', ''),
            "latlng": {"lat": d.get('gps', '')[0], "lng": d.get('gps', '')[1]},
            "country_code": d.get('country_code', ''),
            "rftemplate_id": rf_template_id,
            "networktemplate_id": network_template_id,
            "timezone": d.get('time_zone', ''),
            "sitegroup_ids": check_if_we_need_to_append_gov_wifi_or_moj_wifi_site_groups(
                gov_wifi=d.get('Enable GovWifi', ''),
                moj_wifi=d.get('Enable MoJWifi', ''),
                site_group_ids=json.loads(site_group_ids)
    ),
    }
    # MOJ specific attributes
    site_setting = {

        "auto_upgrade": {
            "enabled": True,
            "version": "custom",
            "time_of_day": "02:00",
            "custom_versions": ap_versions,
            "day_of_week": ""
        },

        "rogue": {
            "min_rssi": -80,
            "min_duration": 20,
            "enabled": True,
            "honeypot_enabled": True,
            "whitelisted_bssids": [
                ""
            ],
            "whitelisted_ssids": [
                "GovWifi"
            ]
        },

        "persist_config_on_device": True,

        "engagement": {
            "dwell_tags": {
                "passerby": "1-300",
                "bounce": "3600-14400",
                "engaged": "25200-36000",
                "stationed": "50400-86400"
            },
            "dwell_tag_names": {
                "passerby": "Below 5 Min (Passerby)",
                "bounce": "1-4 Hours",
                "engaged": "7-10 Hours",
                "stationed": "14-24 Hours"
            },
            "hours": {
                "sun": None,
                "mon": None,
                "tue": None,
                "wed": None,
                "thu": None,
                "fri": None,
                "sat": None
            }
        },
        "analytic": {
            "enabled": True
        },

        "rtsa": {
            "enabled": False,
            "track_asset": False,
            "app_waking": False
        },
        "led": {
            "enabled": True,
            "brightness": 255
        },
        "wifi": {
            "enabled": True,
            "locate_unconnected": True,
            "mesh_enabled": True,
            "mesh_allow_dfs": True
        },

        "switch_mgmt": {
            "use_mxedge_proxy": False,
            "mxedge_proxy_port": "2222"
        },

        "wootcloud": None,
        "skyatp": {
            "enabled": None,
            "send_ip_mac_mapping": None
        },

        "mgmt": {
            "use_wxtunnel": False
        },

        "config_auto_revert": True,
        "status_portal": {
            "enabled": False,
            "hostnames": [
                ""
            ]
        },
        "uplink_port_config": {
            "keep_wlans_up_if_down": True
        },
        "ssh_keys": [],
        "wids": {},
        "mxtunnel": {
            "enabled": False
        },
        "occupancy": {
            "min_duration": None,
            "clients_enabled": False,
            "sdkclients_enabled": False,
            "assets_enabled": False,
            "unconnected_clients_enabled": False
        },
        "public_zone_occupancy": {
            "enabled": False,
            "client_density_enabled": False,
            "rssi_zones_enabled": False
        },
        "zone_occupancy_alert": {
            "enabled": False,
            "threshold": 5,
            "email_notifiers": []
        },
        "gateway_mgmt": {
            "app_usage": False,
            "security_log_source_interface": "",
            "auto_signature_update": {
                "enable": True,
                "time_of_day": "02:00",
                "day_of_week": ""
            }
        },
        "tunterm_monitoring": [],
        "tunterm_monitoring_disabled": True,
        "ssr": {},

        "vars": {
            "site_specific_radius_wired_nacs_secret": d.get('Wired NACS Radius Key', ''),
            "site_specific_radius_govwifi_secret": d.get('GovWifi Radius Key', ''),
            "address": d.get('Site Address', ''),
            "site_name": d.get('Site Name', '')
        }

    }
    return site, site_setting


def plan_of_action(
        data,
        rf_template_id,
        network_template_id,
        site_group_ids
):

    # Generate a timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plan_file_name = "../data_src/mist_plan_{time}.json".format(time=timestamp)
    json_objects = []

    for d in data:
        site, site_setting = build_payload(
            d,
            rf_template_id,
            network_template_id,
            site_group_ids
        )
        json_objects.append(site)
        json_objects.append(site_setting)

    # Load file
    with open(plan_file_name, "w") as plan_file:
        json.dump(json_objects, plan_file, indent=2)

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
    ap_versions = Admin.get_ap_versions()
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
    if ap_versions is None: #or not isinstance(ap_versions, dict):
        raise ValueError('Must provide a valid dictionary for ap_versions')

    # Prompt user if we are using production org_id
    warn_if_using_org_id_production(org_id)

    plan_of_action(
        data,
        rf_template_id,
        network_template_id,
        site_group_ids
    )

    # Establish Mist session
    admin = Admin(mist_username, mist_login_method)

    # Create each site from the CSV file
    for d in data:
        # Variables
        site_id = None

        site, site_setting = build_payload(
            d,
            rf_template_id,
            network_template_id,
            site_group_ids
        )

        print('Calling the Mist Create Site API...')
        result = admin.post('/api/v1/orgs/' + org_id + '/sites', site)
        if result == False:
            print('Failed to create site {}'.format(site['name']))
            print('Skipping remaining operations for this site...')
            print('\n\n==========\n\n')

            continue
        else:
            site_id = result['id']
            print('Created site {} ({})'.format(site['name'], site_id))

            if show_more_details:
                print('\nRetrieving the JSON response object...')
                print(json.dumps(result, sort_keys=True, indent=4))
                print('\nUsing id in the Mist Update Setting API request')

        # Update Site Setting
        print('Calling the Mist Update Setting API...')
        result = admin.put('/api/v1/sites/' + site_id + '/setting',
                           site_setting)
        if result == False:
            print('Failed to update site setting {} ({})'.format(
                site['name'], site_id))
        else:
            print('Updated site setting {} ({})'.format(site['name'], site_id))

            if show_more_details:
                print('\nRetrieving the JSON response object...')
                print(json.dumps(result, sort_keys=True, indent=4))

        print('\n\n==========\n\n')
