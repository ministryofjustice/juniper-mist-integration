import json
from datetime import datetime
import sys


class BuildPayload:
    def __init__(self,
                 data: list,
                 rf_template_id: str,
                 network_template_id: str,
                 site_group_ids: dict,
                 ap_versions: dict):
        self._site_payload = self._build_site_payload(
            data,
            rf_template_id,
            network_template_id,
            site_group_ids,
            ap_versions
        )

    def get_site_payload(self):
        return self._site_payload

    def _validate_data(self, data):
        required_keys = [
            'Site Name',
            'Site Address',
            'gps',
            'country_code',
            'time_zone',
            'Enable GovWifi',
            'Enable MoJWifi'
        ]
        missing_keys = []
        for d in data:
            for required_key in required_keys:
                if required_key in d:
                    pass
                else:
                    missing_keys.append(required_key)
        if missing_keys != []:
            raise ValueError("Missing the following keys {missing_keys}".format(
                missing_keys=missing_keys))

    def _check_if_we_need_to_append_gov_wifi_or_moj_wifi_site_groups(self, gov_wifi, moj_wifi, site_group_ids: dict):
        result = []
        if moj_wifi == 'TRUE':
            result.append(site_group_ids['moj_wifi'])
        if gov_wifi == 'TRUE':
            result.append(site_group_ids['gov_wifi'])
        return result

    def _build_site_payload(
            self,
            data: list,
            rf_template_id: str,
            network_template_id: str,
            site_group_ids: dict,
            ap_versions: dict
    ):
        self._validate_data(data)
        json_objects = []
        for d in data:
            site = {'name': d.get('Site Name', ''),
                    'address': d.get('Site Address', ''),
                    "latlng": {"lat": d.get('gps', '')[0], "lng": d.get('gps', '')[1]},
                    "country_code": d.get('country_code', ''),
                    "rftemplate_id": rf_template_id,
                    "networktemplate_id": network_template_id,
                    "timezone": d.get('time_zone', ''),
                    "sitegroup_ids": self._check_if_we_need_to_append_gov_wifi_or_moj_wifi_site_groups(
                        gov_wifi=d.get('Enable GovWifi', ''),
                        moj_wifi=d.get('Enable MoJWifi', ''),
                        site_group_ids=json.loads(site_group_ids)
            ),
            }

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
                    "mesh_enabled": False,
                    "mesh_allow_dfs": False
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
                    "address": d.get('Site Address', ''),
                    "site_name": d.get('Site Name', '')
                }
            }

            if 'GovWifi Radius Key' in d:
                site_setting["vars"]["site_specific_radius_govwifi_secret"] = d.get(
                    'GovWifi Radius Key')
                site_setting["rogue"]["whitelisted_ssids"] = [
                    "GovWifi"
                ]
            if 'Wired NACS Radius Key' in d:
                site_setting["vars"]["site_specific_radius_wired_nacs_secret"] = d.get(
                    'Wired NACS Radius Key')

            site_dict = {"site": site, "site_setting": site_setting}
            json_objects.append(site_dict)

        return json_objects


def plan_of_action(
    processed_payload
):
    # Generate a timestamp for the filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    plan_file_name = "../data_src/mist_plan_{time}.json".format(time=timestamp)

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
