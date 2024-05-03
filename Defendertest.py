# Import Modules
from azure.identity import DefaultAzureCredential
import json
import csv
import requests
from datetime import datetime

# Authenticate using DefaultAzureCredential
credential = DefaultAzureCredential()

# Replace with your Microsoft Defender API endpoint for listing machines
api_url = 'https://api.securitycenter.microsoft.com/api/machines'

try:
    # Make the API request
    response = requests.get(api_url, headers={'Authorization': 'Bearer ' + credential.get_token('https://api.securitycenter.microsoft.com/.default').token})

    # Check if the request was successful (status code 200)
    response.raise_for_status()

    # Parse the JSON response
    json_data = response.json()

   

    print( json_data)

except requests.exceptions.HTTPError as errh:
    print("HTTP Error:", errh)
except requests.exceptions.ConnectionError as errc:
    print("Error Connecting:", errc)
except requests.exceptions.Timeout as errt:
    print("Timeout Error:", errt)
except requests.exceptions.RequestException as err:
    print("Request Exception:", err)
