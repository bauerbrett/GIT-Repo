#Import all the modules
import csv
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from datetime import datetime

#This is the credentail that is being used in CLI. Run az login to get it.
credential = DefaultAzureCredential()

#List data for file name
current_date = datetime.now().strftime("%Y.%m.%d")

#Define list_blobs function
def list_blobs(container_name):
    blob_service_client = BlobServiceClient(account_url="https://", credential=credential)
    container_client = blob_service_client.get_container_client(container_name)
    
    #List blobs from container client
    blob_list = container_client.list_blobs()

    #Put blob data in dictionary.
    blobs_data = []

    print("Blobs in container:")

    #For each blob in the list get the information we need.
    for blob in blob_list:
        blob_client = container_client.get_blob_client(blob)
        blob_properties = blob_client.get_blob_properties()
        created_date = blob_properties['creation_time']
        last_modified_data = blob_properties['last_modified']
        print(f"Blob Name: {blob.name} - Created: {created_date} - Last Modified: {last_modified_data}")

        #Put the info we need in a list
        blob_info = {
            "Container Name": container_name,
            "Blob Name": blob.name,
            "Created Date": created_date,
            "Last Modified Date": last_modified_data
        }
        
        #Join the two together
        blobs_data.append(blob_info)

    #Return it so we can ues it in csv
    return blobs_data

#Create the main function
def main():

    blob_container = "wcore"

    blobs_data = list_blobs(blob_container) #Use the list_blobs function with the blob_container name

    output_directory = r'C:\Users'

    csv_file_path = f'{output_directory}\\{current_date}.CoreBackup.csv'


    #Write the returned blob data into a csv file
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Container Name", "Blob Name", "Created Date", "Last Modified Date"])
        writer.writeheader()
        writer.writerows(blobs_data)

    print(f"Blobs information exported to {csv_file_path}")

if __name__ == "__main__":
    main()