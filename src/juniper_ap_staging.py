from juniper_client import JuniperClient
from build_juniper_payload import plan_of_action


def validate_if_site_defined_on_csv_exists_in_mist(mist_sites_configs: list['dict'],
                                                   ap_csv: list['dict']):
    mist_site_names = []
    for mist_site_config in mist_sites_configs:
        mist_site_names.append(mist_site_config['name'])

    mist_site_names_csv_file = []
    for ap_row in ap_csv:
        mist_site_names_csv_file.append(ap_row['Site Name'])

    for site_name in mist_site_names_csv_file:
        if site_name not in mist_site_names:
            raise ValueError(
                f"Site name '{site_name}' found in CSV file but not in mist site configurations.")


def validate_if_ap_defined_on_csv_exists_in_mist(mist_inventory: list['dict'],
                                                 ap_csv: list['dict']):
    ap_mac_addresses_from_mist = []
    for inventory_item in mist_inventory:
        if inventory_item['type'] == 'ap':
            ap_mac_addresses_from_mist.append(inventory_item['mac'].upper())

    ap_mac_addresses_from_csv = []
    for ap_row in ap_csv:
        cleaned_mac_address = ap_row['MAC Address'].replace(":", "")
        ap_mac_addresses_from_csv.append(cleaned_mac_address)

    for ap_mac_address in ap_mac_addresses_from_csv:
        if ap_mac_address.upper() in ap_mac_addresses_from_mist:
            continue
        else:
            raise ValueError(
                f"AP Mac address '{ap_mac_address}' found in CSV file but not on mist inventory.")


def find_site_by_name(site_name: str,
                      site_and_mac_reservations: list):
    for site in site_and_mac_reservations:
        if site["SiteName"] == site_name:
            return site
    return None


def format_site_and_mac_reservations(ap_csv: list['dict']
                                     ) -> list['dict']:
    site_and_mac_reservations = []

    for ap_row in ap_csv:
        site_name = ap_row.get("Site Name", "")
        mac_address = ap_row.get("MAC Address", "").replace(":", "")

        # Find the existing site in the list
        existing_site = find_site_by_name(site_name, site_and_mac_reservations)

        if existing_site:
            # Update the mac_addresses field by appending the new MAC address
            if mac_address not in existing_site["mac_addresses"]:
                existing_site["mac_addresses"].append(mac_address.lower())
        else:
            # Create a new dictionary with the desired keys and values
            new_item = {
                ""
                "SiteName": site_name,
                "mac_addresses": [mac_address.lower()]
            }
            # Append the new dictionary to the output list
            site_and_mac_reservations.append(new_item)

    return site_and_mac_reservations


def find_site_id(
        site_and_mac_reservations_without_mist_site_ids: list['dict'],
        mist_sites_configs: list['dict']
) -> list['dict']:

    for site_csv in site_and_mac_reservations_without_mist_site_ids:
        site_found = False
        for site_mist in mist_sites_configs:
            if site_csv['SiteName'] == site_mist['name']:
                site_csv['site_id'] = site_mist['id']
                site_found = True
                break
        if not site_found:
            raise ValueError(
                f"No matching site_id found for site: {site_csv['SiteName']}")

    return site_and_mac_reservations_without_mist_site_ids


def get_site_payload_for_inventory_assign_to_site(
        site_and_mac_reservations_including_mist_site_ids: list['dict']
) -> list['dict']:
    payload = []

    for site in site_and_mac_reservations_including_mist_site_ids:
        payload.append(
            {
                "op": "assign",
                "site_id": site['site_id'],
                "macs": site['mac_addresses'],
                "no_reassign": False,
                "disable_auto_config": False,
                "managed": False
            }
        )

    return payload


def rename_ap(admin: object,
              site_id: str,
              ap_id: str,
              new_ap_name: str):
    api_url = '/api/v1/sites/' + site_id + '/devices/' + ap_id
    response = admin.put(api_url, payload={'name': new_ap_name})
    if response == False:
        print('Failed to rename ap to new desired name {}'.format(new_ap_name))
    else:
        print('Successfully renamed ap to new desired name {}'.format(new_ap_name))


def build_rename_ap_payload(
        inventory_payloads: list['dict'],
        mist_inventory: list['dict'],
        ap_csv: list['dict']
) -> list['dict']:
    payload = []

    for site in inventory_payloads:
        for mac in site['macs']:
            inventory_item = find_inventory_item_by_mac_address(
                mist_inventory, mac)
            csv_item = find_csv_item_by_mac_address(ap_csv, mac)
            payload.append(
                {
                    "new_ap_name": csv_item['Host Name'],
                    "site_id": site['site_id'],
                    "ap_id": inventory_item['id'],
                }
            )

    return payload


def find_value_in_list_of_dicts(list_of_dicts, key, value):
    for dictionary in list_of_dicts:
        if dictionary.get(key) == value:
            return dictionary
    raise ValueError(
        f"Value '{value}' not found for key '{key}' in the list of dictionaries.")


def find_inventory_item_by_mac_address(
        mist_inventory: list['dict'],
        mac: str
) -> dict:

    try:
        result = find_value_in_list_of_dicts(mist_inventory, "mac", mac)
        return result
    except ValueError as e:
        print(e)


def find_csv_item_by_mac_address(
        ap_csv: list['dict'],
        mac: str
) -> list[dict]:

    try:
        result = find_value_in_list_of_dicts(
            ap_csv, "MAC Address", mac.upper())
        return result
    except ValueError as e:
        print(e)


def juniper_ap_assign(
        ap_csv: list['dict'],
        org_id=None,
        mist_username=None,
        mist_login_method=None
):
    admin = JuniperClient(mist_username, mist_login_method)
    mist_sites_configs = admin.get('/api/v1/orgs/' + org_id + '/sites')
    mist_inventory = admin.get('/api/v1/orgs/' + org_id + '/inventory')

    validate_if_site_defined_on_csv_exists_in_mist(mist_sites_configs, ap_csv)
    validate_if_ap_defined_on_csv_exists_in_mist(mist_inventory, ap_csv)

    site_and_mac_reservations_without_mist_site_ids = format_site_and_mac_reservations(
        ap_csv
    )

    site_and_mac_reservations_including_mist_site_ids = find_site_id(
        site_and_mac_reservations_without_mist_site_ids,
        mist_sites_configs
    )

    inventory_payloads = get_site_payload_for_inventory_assign_to_site(
        site_and_mac_reservations_including_mist_site_ids)

    plan_of_action(inventory_payloads)

    for site_payload in inventory_payloads:
        result = admin.put('/api/v1/orgs/' + org_id +
                           '/inventory', site_payload)
        if result == False:
            print('Failed to assign ap {}'.format(site_payload))
        else:
            print('Successfully assigned ap {}'.format(site_payload))

    rename_ap_payload = build_rename_ap_payload(
        inventory_payloads, mist_inventory, ap_csv)
    plan_of_action(rename_ap_payload)

    for ap_item in rename_ap_payload:
        rename_ap(
            admin,
            ap_item['site_id'],
            ap_item['ap_id'],
            ap_item['new_ap_name']
        )
