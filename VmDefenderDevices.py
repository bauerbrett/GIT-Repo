# Import Module
from azure.identity import DefaultAzureCredential
import json
import csv
import requests
from datetime import datetime
import os


# Authenticate using Default Azure Credential
credential = DefaultAzureCredential()

# Replace with your Microsoft Defender API endpoint for listing machines
api_url = 'https://api.securitycenter.microsoft.com/api/machines'

try:
    # Make the API request
    token = credential.get_token('https://api.securitycenter.microsoft.com/.default')
    response = requests.get(api_url, headers={'Authorization': 'Bearer ' + token.token})

    # Check if the request was successful (status code 200)
    response.raise_for_status()

    # Parse the JSON response
    json_data = response.json()

    # Extract specific fields for each item in the JSON data
    data_to_export = []

    for item in json_data.get('value', []):
        computer_dns_name = item.get('computerDnsName', '')
        health_status = item.get('healthStatus', '')
        exposure_level = item.get('exposureLevel', '')
        risk_score = item.get('riskScore', '')
        last_seen = item.get('lastSeen', '')

        # Skip entries with inactive health status. This will block old machines that are not used anymore.
        if health_status.lower() == 'inactive':
            continue

        # Adding the extracted fields to the list for CSV
        row = {
            'Computer DNS Name': computer_dns_name,
            'Health Status': health_status,
            'Exposure Level': exposure_level,
            'Risk Score': risk_score,
            'Last Seen': last_seen
        }
        data_to_export.append(row)

    # Specify the CSV file directory
    output_directory = r'C:\Users\BrettBauer\Anti-Virus Software Check\2024'

    # Specify the CSV file path
    current_date = datetime.now().strftime("%Y.%m.%d")
    csv_file_path = f'{output_directory}\\{current_date}.testDefenderMachineListing.csv'

    # Write data to CSV file
    with open(csv_file_path, 'w', newline='') as csv_file:
        fieldnames = ['Computer DNS Name', 'Health Status', 'Exposure Level', 'Risk Score', 'Last Seen']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Write header
        writer.writeheader()

        # Write rows
        writer.writerows(data_to_export)

    print(f'Data exported to {csv_file_path}')

except requests.exceptions.HTTPError as errh:
    print("HTTP Error:", errh)
except requests.exceptions.ConnectionError as errc:
    print("Error Connecting:", errc)
except requests.exceptions.Timeout as errt:
    print("Timeout Error:", errt)
except requests.exceptions.RequestException as err:
    print("Request Exception:", err)