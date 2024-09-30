import requests
import pandas as pd
import logging
from base64 import b64encode
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import getpass

def get_jira_filters(userName, token, baseUrl, api_version):
    """
    Get all filters from the Jira instance and return them as a list of dictionaries.

    :param userName: Jira username
    :param token: Jira API token or password
    :param baseUrl: Base URL of the Jira instance
    :param api_version: API version to use (v2 or v3)
    :return: List of dictionaries containing filter details
    """
    auth_string = f"{userName}:{token}".encode('utf-8')
    headers = {
        "Authorization": f"Basic {b64encode(auth_string).decode('utf-8')}",
        "Content-Type": "application/json"
    }

    filters = []
    start_at = 0
    max_results = 50
    is_last = False

    while not is_last:
        url = f"{baseUrl}/rest/api/{api_version}/filter/search?startAt={start_at}&maxResults={max_results}"
        logging.info(f"Fetching filters from: {url}")
        response = requests.get(url, headers=headers)
        logging.debug(f"Response status code: {response.status_code}")
        
        if response.status_code != 200:
            logging.error(f"Failed to fetch filters: {response.text}")
            break
        
        data = response.json()
        logging.debug(f"Response data: {data}")

        if 'values' not in data:
            logging.error(f"Unexpected response format: {data}")
            break

        filters.extend(data['values'])
        start_at += max_results
        is_last = data.get('isLast', True)

    return filters

def fetch_filter_details(filter_id, headers, baseUrl, api_version):
    """
    Fetch detailed information for a single filter.

    :param filter_id: The ID of the filter
    :param headers: The headers for the API request
    :param baseUrl: Base URL of the Jira instance
    :param api_version: API version to use (v2 or v3)
    :return: A dictionary containing filter details
    """
    url = f"{baseUrl}/rest/api/{api_version}/filter/{filter_id}"
    logging.debug(f"Fetching filter details from: {url}")
    response = requests.get(url, headers=headers)
    logging.debug(f"Response status code: {response.status_code}")

    if response.status_code != 200:
        logging.error(f"Failed to fetch filter details: {response.text}")
        return None

    filter_data = response.json()
    logging.debug(f"Filter details: {filter_data}")
    return filter_data

def format_permissions(permissions):
    """
    Format the permissions field into a readable string.

    :param permissions: List of dictionaries containing permissions
    :return: Formatted string of user names, group names, and project roles
    """
    formatted_permissions = []

    for perm in permissions:
        if perm.get('type') == 'user':
            formatted_permissions.append(perm['user']['displayName'])
        elif perm.get('type') == 'group':
            formatted_permissions.append(f"Group: {perm['group']['name']}")
        elif perm.get('type') == 'projectRole':
            formatted_permissions.append(f"Project Role: {perm['projectRole']['name']}")

    return ", ".join(formatted_permissions)

def save_filters_to_csv(filter_details, filename):
    """
    Save filter details to a CSV file.

    :param filter_details: List of dictionaries containing filter details
    :param filename: Name of the CSV file
    """
    if not filter_details:
        logging.warning("No filter details to save.")
        return

    data = []
    for filter in filter_details:
        if filter is None:
            continue
        filter_info = {
            "Filter name": filter['name'],
            "Owner": filter['owner']['displayName'],
            "Share Permissions": format_permissions(filter['sharePermissions']),
            "Edit Permissions": format_permissions(filter['editPermissions']),
            "Is Writable": filter['isWritable'],
            "Approximate Last Used": filter.get('approximateLastUsed', None)
        }
        data.append(filter_info)

    df = pd.DataFrame(data)
    logging.info(f"Saving data to CSV: {filename}")
    df.to_csv(filename, index=False)

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    instance_type = input("Enter instance type (cloud/server): ").strip().lower()
    baseUrl = input("Enter Jira instance URL: ").strip()
    userName = input("Enter username: ").strip()
    if instance_type == "cloud":
        token = getpass.getpass("Enter API key: ").strip()
        api_version = "3"
    else:
        token = getpass.getpass("Enter password: ").strip()
        api_version = "2"
    filename = "jira_filters.csv"

    logging.info("Starting the Jira filter fetching process.")
    logging.info(f"Using instance type: {instance_type}")
    logging.info(f"Using baseUrl: {baseUrl}")
    logging.info(f"Using userName: {userName}")

    filters = get_jira_filters(userName, token, baseUrl, api_version)
    if not filters:
        logging.warning("No filters found.")
        return

    auth_string = f"{userName}:{token}".encode('utf-8')
    headers = {
        "Authorization": f"Basic {b64encode(auth_string).decode('utf-8')}",
        "Content-Type": "application/json"
    }

    filter_details = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_filter_details, filter['id'], headers, baseUrl, api_version) for filter in filters]

        for future in tqdm(as_completed(futures), total=len(futures), desc="Fetching Filter Details"):
            result = future.result()
            if result is not None:
                filter_details.append(result)

    save_filters_to_csv(filter_details, filename)
    print(f"Filter details saved to {filename}")

if __name__ == "__main__":
    main()
