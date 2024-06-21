#This is a script to mass enable Sentinel anayltic rules from content package templates. 
#Most of it is from a person on the internet named Steve Pye.
#Tweaked it some to fit my needs.

#Just add your subscription id, resource group name, workspace name, and content package name. It will enable most the rules for you. 
#A few rules will throw errors but this should get most of them.

from azure.identity import DefaultAzureCredential
import requests
#from azure.mgmt.securityinsight import SecurityInsights
import json


#Change these values to wherever you Sentinel instance lives.
credential = DefaultAzureCredential()
subscription_id = ""
resource_group_name = ""
workspace_name = ""
api_version = "2024-03-01" #Grab latest version from api reference docs
solution_name = ""
enable_rules = True #If this is false it will create the rules but not enable them right away.


def enable_rules():
    """Enable analytic rules that are in your installed content packages from the content hub."""
    try:
        #Create token to make requests
        token = credential.get_token("https://management.azure.com/.default").token

        #Get content packages 
        content_uri = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.OperationalInsights/workspaces/{workspace_name}/providers/Microsoft.SecurityInsights/contentProductPackages?api-version={api_version}"

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
            }

        content_packages = requests.get(content_uri, headers=headers)

        if content_packages.status_code == "404":
            print(f"Error: {content_packages.status_code} - URL not found: {content_uri}")
        else:
            content_packages = content_packages.json()

        #for response in content_packages.get("value", []):
            #print(f"{response}\n")


        solutions = [s for s in content_packages.get('value', [])]
        solution = next((s for s in solutions if s['properties']['displayName'] == solution_name), None)
        if not solution:
                    raise Exception(f"Solution Name: [{solution_name}] cannot be found. Please check the solution name and Install it from the Content Hub blade")
        #print(solution)
        #Get content templates

        content_templates_uri = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.OperationalInsights/workspaces/{workspace_name}/providers/Microsoft.SecurityInsights/contentTemplates?api-version={api_version}"

        content_templates = requests.get(content_templates_uri, headers=headers)

        if content_templates.status_code == "404":
            print(f"Error: {content_templates.status_code} - URL not found: {content_templates_uri}")
        else:
            content_templates = content_templates.json()

        content_temps = [content for content in content_templates.get("value", None)]

        templates = [content for content in content_temps if content.get("properties").get("packageId") == solution['properties']['contentId']
                        and content.get("properties").get("contentKind") == "AnalyticsRule"]

        print(f"{len(templates)} Analytic Rules for {solution_name.title()}")

        template_Names = [temp["name"] for temp in templates]

        for template_Name in template_Names:
            #print(f"{template_Name}\n")
            rule_template_uri = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.OperationalInsights/workspaces/{workspace_name}/providers/Microsoft.SecurityInsights/contentTemplates/{template_Name}?api-version={api_version}"
                
            rule_response = requests.get(rule_template_uri, headers=headers).json()

            #print(json.dumps(rule_template_response, indent=4))

        #client = SecurityInsights(credential=token, subscription_id=subscription_id)

            rule_properties = next((response["properties"] for response in rule_response.get("properties", {}).get("mainTemplate", {}).get("resources", []) if 
                                    response.get("type", None) == "Microsoft.OperationalInsights/workspaces/providers/metadata"), None)
            
            if rule_properties:
                rule_properties.pop("description", None)
                rule_properties.pop("parentId", None)

            rule = next((response for response in rule_response.get("properties", {}).get("mainTemplate", {}).get("resources", [])
                        if response.get("type") == "Microsoft.SecurityInsights/AlertRuleTemplates"), None)
            
            if rule:
                rule["properties"]["alertRuleTemplateName"] = rule["name"]
                rule["properties"]["templateVersion"] = rule_response.get('properties', {}).get('version')

            if enable_rules:
                rule["properties"]["enabled"] = True

            rule_payload = json.dumps(rule, separators=(',', ':'))

            rule_uri = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.OperationalInsights/workspaces/{workspace_name}/providers/Microsoft.SecurityInsights/alertRules/{rule["name"]}?api-version={api_version}"

            try:
                rule_create = requests.put(rule_uri, headers=headers, data=rule_payload)
            
                rule_create.raise_for_status()
                if rule_create.status_code not in [200, 201]:
                        raise Exception(f"Error when enabling Analytics rule: {rule['properties']['displayName']}")
                    
                if enable_rules:
                    print(f"Creating and Enabling Analytic rule: {rule['properties']['displayName']}")
                else:
                    print(f"Creating Analytic rule: {rule['properties']['displayName']}")

                rule_response = rule_create.json()

                rule_properties["parentId"] = rule_response["id"]

                # Correct the metadata type to Microsoft.SecurityInsights/metadata
                metadata_payload = {
                    "properties": rule_properties
                }
                metadata_payload = json.dumps(metadata_payload, separators=(',', ':'))

                metadata_uri = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.OperationalInsights/workspaces/{workspace_name}/providers/Microsoft.SecurityInsights/metadata/analyticsrule-{rule['name']}?api-version={api_version}"

                metadata_result = requests.put(metadata_uri, headers=headers, data=metadata_payload)

                metadata_result.raise_for_status()
                if metadata_result.status_code not in [200, 201]:
                    raise Exception(f"Error when update metadata for rule: {rule["properties"]["displayName"]}")
                else:
                    print(f"Updated metadata for rule: {rule["properties"]["displayName"]}")

            except Exception as e:
                print(f"Error: {e}")
    except Exception as e:
         print(f"Error: {e}")


def main():
     
    enable_rules()

if __name__ == "__main__":
     main()