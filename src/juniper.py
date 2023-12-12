import requests
import json

# Mist CRUD operations

class Admin:

    def login_via_username_and_password(self, username, password):
        login_url = self.base_url + "/login"
        login_payload = {'email': username, 'password': password}
        self.session.post(login_url, data=login_payload)
        mfa_headers = {
            'X-CSRFToken': self.session.cookies.get('csrftoken.eu'),  # Include CSRF token in headers
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
            raise ValueError("Login was not successful: {response}".format(response=login_response))

    def login_via_token(self, token):
        self.headers['Authorization'] = 'Token ' + token
        request_url = self.base_url + "/self/apitokens"
        responce = self.session.get(request_url, headers=self.headers)
        if responce.status_code == 200:
            print("Login successful")
        else:
            raise ValueError("Login was not successful via token: {response}".format(response=responce))



    def __init__(self, token=None, username=None, password=None):
        self.session = requests.Session()
        self.headers = {'Content-Type': 'application/json'}
        self.base_url = 'https://api.eu.mist.com/api/v1'

        if token:
            self.login_via_token(token)
        elif username and password:
            self.login_via_username_and_password(username, password)
        else:
            raise ValueError("Invalid parameters provided for authentication.")

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
            print('\tResponse: {} ({})'.format(response.text, response.status_code))
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
            print('\tResponse: {} ({})'.format(response.text, response.status_code))
            return False

        return json.loads(response.text)

def check_if_we_need_to_append_gov_wifi_or_moj_wifi_site_groups(gov_wifi, moj_wifi, site_group_ids: dict):
    result = []
    if moj_wifi == 'TRUE':
        result.append(site_group_ids['moj_wifi'])
    if gov_wifi == 'TRUE':
        result.append(site_group_ids['gov_wifi'])
    return result


# Main function
def juniper_script(
        data,
        mist_api_token=None,
        org_id=None,
        mist_username=None,
        mist_password=None,
        site_group_ids=None
):

    # Configure True/False to enable/disable additional logging of the API response objects
    show_more_details = True
    # Check for required variables
    if org_id is None or org_id == '':
        raise ValueError('Please provide Mist org_id')
    if (mist_api_token is None ) and (mist_username is None or mist_password is None):
        raise ValueError('No authentication provided, provide mist username and password or API key')
    if site_group_ids is None:
        raise ValueError('Must provide site_group_ids for GovWifi & MoJWifi')

    # Establish Mist session
    admin = Admin(mist_api_token, mist_username, mist_password)

    # Create each site from the CSV file
    for d in data:
        # Variables
        site_id = None
        site = {'name': d.get('Site Name', ''),
                'address': d.get('Site Address', ''),
                "latlng": {"lat": d.get('gps', '')[0], "lng": d.get('gps', '')[1]},
                "country_code": d.get('country_code', ''),
                "rftemplate_id": "8542a5fa-51e4-41be-83b9-acb416362cc0",
                "timezone": d.get('time_zone', ''),
                "sitegroup_ids": check_if_we_need_to_append_gov_wifi_or_moj_wifi_site_groups(
                    gov_wifi=d.get('Enable GovWifi', ''),
                    moj_wifi=d.get('Enable MoJWifi', '' ),
                    site_group_ids=json.loads(site_group_ids)
                ),
                }

        # MOJ specific attributes
        site_setting = {

            "vars": {
                "site_specific_radius_wired_nacs_secret": d.get('Wired NACS Radius Key', ''),
                "site_specific_radius_govwifi_secret": d.get('GovWifi Radius Key', ''),
                "address": d.get('Site Address', ''),
                "site_name": d.get('Site Name', '')
            },


        }

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

        print()

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
