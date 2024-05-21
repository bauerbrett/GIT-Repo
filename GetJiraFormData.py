#This script was made to grab form answers from Jira ITSM tickets and send an email based off the data found.\
#It can be customized to grab any answer off forms, you just need to know what the form looks like so you can grab 
#data from the dictonaries that are inside the list the response shoots out.

import requests
from requests.auth import HTTPBasicAuth
import json
import os
import win32com.client as win32
from jira import JIRA
from datetime import datetime, timedelta

#Current Date to do conditionals on software renewals
current_date = datetime.today()

#Jira Domain
jira_domain = ""

#api token
api_token = os.environ.get('Jira_API_Key')

#Email to use in auth
email = ""

#Autenticate with email and api token. Use domain as the server
jira = JIRA(basic_auth=(email, api_token), options={"server": jira_domain})

#Prject id
project = "Security"

#issue_type = 'Service request'
label = "Software_Requests"

#Cloud ID to use with Jira API
cloud_id = ""

def get_issue_keys():

    #Create key list with issue keys 
    #Create summary list with summary of issue
    issue_keys = []
    summary_list = []
     # Search issues
    issues_in_proj = jira.search_issues(f'Labels={label} AND project={project}', fields=f"key, summary", maxResults=False)
    
    

    # Process and print issues
    for issue in issues_in_proj:
        issue_key = issue.key
        summary = issue.fields.summary
        summary = summary.removeprefix("Software Request - ")

        issue_keys.append({
            "Summary": summary,
            "Issue Key": issue_key
        })
    #print(issue_keys)

    return issue_keys
    

def get_uuid(issue_keys):

    for item in issue_keys:

        issue_key = item.get("Issue Key")

        url = f"{jira_domain}/rest/api/2/issue/{issue_key}/properties/proforma.forms"

        auth = HTTPBasicAuth(email, api_token)

        headers = {
        "Accept": "application/json",
        "X-ExperimentalApi": "opt-in"
        }

        response = requests.request(
        "GET",
        url,
        headers=headers,
        auth=auth
        )

        #print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))

        response = response.json()

        #Put the UUID of form in the dictionaries
        for item1 in response.get("value")["forms"]:
             item["UUID"] = item1["uuid"]

          
    return issue_keys

def get_form_info(issue_keys2):

    indices_to_remove = []

    for i, item in enumerate(issue_keys2):
        #print(f"Index: {i}, Item: {item}")
        issue_key = item.get('Issue Key')  # Get the issue key for the current item
        uuid = item.get("UUID")
        url = f"https://api.atlassian.com/jira/forms/cloud/{cloud_id}/issue/{issue_key}/form/{uuid}/format/answers"

        auth = HTTPBasicAuth(email, api_token)

        headers = {
            "Accept": "application/json",
            "X-ExperimentalApi": "opt-in"
        }

        response = requests.get(url, headers=headers, auth=auth)

        if response.status_code == 200:
            response1 = response.json()
            # Debug print for response
            #print(f"Response for issue key {item['Issue Key']}: {response1}")

            # Initialize variables to store the form data
            description = contract_type = owner = cost = renew_date_without_zeros = days_left = None

            # Ensure the response is a list of dictionaries
            if isinstance(response1, list):
                for response_item in response1: #For each response do this stuff below
                    if response_item.get("label") == "Contract Renewal Date:": #The response is a weird format. Label is the key and the question is the value in the dict.
                        try:
                            renew = response_item.get("answer")
                            renew_date_str = renew.split('T')[0]  # Extracting the date part
                            renew_datetime = datetime.strptime(renew_date_str, "%Y-%m-%d")
                            renew_date_without_zeros = renew_datetime.strftime('%Y-%m-%d')  # Formatting without trailing zeros
                            days_left = (renew_datetime - current_date).days
                        except ValueError:
                            print(f"Error parsing date for issue {item['Issue Key']}")
                            days_left = None
                        print(f"Days left: {days_left}")
                        print(f"Renewal date: {renew_date_without_zeros}")

                    if response_item.get("label") == "Estimated Annual Cost":
                        cost = response_item.get("answer")
                        cost = cost.removeprefix("$") #Going to put this in email because some have the $ and some do not.
                        #print(f"Cost: {cost}"
                        
                    if response_item.get("label") == "Department Owner":
                        owner = response_item.get("answer")
                        #print(f"Department Owner: {owner}")
                    
                    if response_item.get("label") == "Contract Type":
                        contract_type = response_item.get("answer")
                        #print(f"Contract Type: {contract_type}")

                    if response_item.get("label") == "Description & Business Justification": 
                        description = response_item.get("answer")
                        #print(f"Description & Business Justification: {description}")
                    else:
                        if response_item.get("label") == "Business Justification and Description of Software": 
                            description = response_item.get("answer")
                    
                
            # For this we want the pieces of software that are coming up for nenewal in 90 days. 
            if days_left is None or days_left > 90:
                #print(f"Removing issue with key {item['Issue Key']} due to days_left = {days_left}")
                indices_to_remove.append(i) #Put the index i in a list. You can call back to this list later to remove those item from list.
            else: #If it matches add these key/pairs to the dictionary. 
                issue_keys2[i]["Department Owner"] = owner
                issue_keys2[i]["Cost"] = cost
                issue_keys2[i]["Renewal Date"] = renew_date_without_zeros
                issue_keys2[i]["Days Until Renewal"] = days_left
                issue_keys2[i]["Contract Type"] = contract_type
                issue_keys2[i]["Description & Business Justification"] = description
                
                #print(f"Updated item: {issue_keys2[i]}")
        else:
            print(f"Failed to retrieve form data for issue {item['Issue Key']}: {response.status_code}")
    
    # Remove items with collected indices in reverse order. You want to reverse so the largest numbers are first. That way we remove items from back to front.
    for index in sorted(indices_to_remove, reverse=True):
        del issue_keys2[index]

    #print("Final issue keys list:", issue_keys2) # You can use this to check your dictionaries at the end and make sure it looks correct.

    #Return the list to use in the next function
    return issue_keys2 

#Create funciton to send email. Add the list you returned as the object passed through.
def send_outlook_email(email_list_items):

    recipient_email = ""
    subject = "IT Tool Renewal Alert Test"

    outlook = win32.Dispatch("Outlook.Application")
    o1NS = outlook.GetNameSpace("MAPI")
    mail = outlook.CreateItem(0)  # 0 represents the index of the item type (0 for MailItem)

    # Set email properties
    mail.Subject = subject
    mail.To = recipient_email
    mail.BodyFormat = 1
    mail.Sender = ""
    mail.body = "Hello,\n\nHere are the IT tools that are coming up for renewal:\n"

    #Loop for the list of dictionaries and put those items in the body
    for issue in email_list_items:
        mail.body += f"\n\nSoftware Name: {issue['Summary']}\n\t- Department Owner: {issue['Department Owner']}\n\t- Renewal Date: {issue['Renewal Date']}\n\t- Days Until Renewal: {issue['Days Until Renewal']}\n"\
        f"\t- Estimated Annual Cost: ${issue['Cost']}\n\t- Contract Type: {issue["Contract Type"]}\n\t- Description & Business Justification: {issue["Description & Business Justification"]}"
    mail.body += f"\n\nThanks,\n Brett Bauer"
    # Send the email
    mail.Send()

#Create main function to run the script.
def main():
    
    issue_keys = get_issue_keys()

    issue_keys2 = get_uuid(issue_keys)

    email_list_items = get_form_info(issue_keys2)

    send_outlook_email(email_list_items)

if __name__ == "__main__":
    main()
