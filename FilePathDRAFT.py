import logging
import requests
from azure.identity import DefaultAzureCredential

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define your authentication parameters
resource = 'https://api.securitycenter.microsoft.com'

# Get access token using DefaultAzureCredential
credential = DefaultAzureCredential()

# Function to fetch disk paths and registry paths for software inventory of a machine
def fetch_paths(machine_id):
    try:
        print("Inside try block")
        access_token = credential.get_token(resource).token

        # Set headers with authorization token
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        # Construct URL with query parameters
        url = f"https://api.securitycenter.microsoft.com/api/machines/SoftwareInventoryByMachine?pageSize=5&sinceTime=2021-05-19T18%3A35%3A49.924Z"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        software_inventory_data = response.json().get('value', [])

        # Filter software inventory data for the given machine ID
        software_data = [item for item in software_inventory_data if item.get('testdeviceId') == machine_id]

        # Print disk paths and registry paths for each software
        for item in software_data:
            disk_paths = ', '.join(item.get('diskPaths', []))
            registry_paths = ', '.join(item.get('registryPaths', []))
            print(f"Software: {item.get('softwareName')}, Disk Paths: {disk_paths}, Registry Paths: {registry_paths}")
    except Exception as e:
        print(f"Error: {e}")

# Call fetch_paths function with a specific machine ID
fetch_paths("")
