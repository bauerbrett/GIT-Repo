import csv
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from datetime import datetime
import requests
import base64

# This is the credential that is being used in CLI. Run az login to get it.
credential = DefaultAzureCredential()

# List data for the file name
current_date = datetime.now().strftime("%Y.%m.%d")

output_directory = r'C:\Users\BrettBauer\2024'
csv_file_path = f'{output_directory}\\{current_date}.CoreBackup.csv'

# Define list_blobs function
def list_blobs(container_name):
    blob_service_client = BlobServiceClient(account_url="['Place here']", credential=credential)
    container_client = blob_service_client.get_container_client(container_name)

    # List blobs from container client
    blob_list = container_client.list_blobs()

    # Put blob data in dictionary.
    blobs_data = []

    print("Blobs in container:")

    # For each blob in the list, get the information we need.
    for blob in blob_list:
        blob_client = container_client.get_blob_client(blob)
        blob_properties = blob_client.get_blob_properties()
        created_date = blob_properties['creation_time']
        last_modified_data = blob_properties['last_modified']
        print(f"Blob Name: {blob.name} - Created: {created_date} - Last Modified: {last_modified_data}")

        # Put the info we need in a list
        blob_info = {
            "Container Name": container_name,
            "Blob Name": blob.name,
            "Created Date": created_date,
            "Last Modified Date": last_modified_data
        }

        # Join the two together
        blobs_data.append(blob_info)

    # Return it so we can use it in csv
    return blobs_data

# Create the main function
def main():
    blob_container = "core"
    blobs_data = list_blobs(blob_container)


    # Write the returned blob data into a csv file
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Container Name", "Blob Name", "Created Date", "Last Modified Date"])
        writer.writeheader()
        writer.writerows(blobs_data)

    print(f"Blobs information exported to {csv_file_path}")

    # Send email using Microsoft Graph API
    send_email(credential, csv_file_path)


def send_email(credential, csv_file_path):
    token = credential.get_token('https://graph.microsoft.com/.default')

    graph_api_endpoint = "https://graph.microsoft.com/v1.0/me/sendMail"

    recipient_email = "brettbauer@lifespeak.com"
    subject = "Blob Information Exported"

    # Read the CSV file content and encode it in base64
    with open(csv_file_path, 'rb') as csv_file:
        csv_content_base64 = base64.b64encode(csv_file.read()).decode('utf-8')

    body = {
        "contentType": "Text",
        "content": f"Blobs information has been exported. See attached CSV file."
    }

    email_payload = {
        "message": {
            "subject": subject,
            "body": body,
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": recipient_email
                    }
                }
            ],
            "attachments": [
                {
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": "Backup.csv",
                    "contentBytes": csv_content_base64
                }
            ]
        },
        "saveToSentItems": "true"
    }

    headers = {
        "Authorization": f"Bearer {token.token}",
        "Content-Type": "application/json",
    }

    response = requests.post(graph_api_endpoint, json=email_payload, headers=headers)

    if response.status_code == 202:
        print("Email sent successfully!")
    else:
        print(f"Failed to send email. Status code: {response.status_code}, Response text: {response.text}")

# ...

if __name__ == "__main__":
    main()