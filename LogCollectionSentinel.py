import requests
import json
import pyodbc

# Query SQL Server Logs with Python

# Establish connection to SQL Server
connection_string = 'DRIVER={SQL Server};SERVER=your_server;DATABASE=your_database;UID=your_username;PWD=your_password'
conn = pyodbc.connect(connection_string)

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Define SQL query
sql_query = """
SELECT Timestamp, LogLevel, Message
FROM ApplicationLogs
WHERE Timestamp >= '2022-01-01' AND LogLevel IN ('Error', 'Warning')
"""

# Execute the query
cursor.execute(sql_query)

# Fetch results
logs = cursor.fetchall()

# Close the cursor and connection
cursor.close()
conn.close()

# Step 5: Send Logs to Log Analytics Workspace

# Define Log Analytics workspace details
workspace_id = 'your_workspace_id'
workspace_key = 'your_workspace_key'
api_version = '2016-04-01'

# Define Log Analytics Data Collector API endpoint
api_endpoint = f'https://<workspace_name>.ods.opinsights.azure.com/api/logs?api-version={api_version}'

# Prepare logs in the required format
formatted_logs = []
for log in logs:
    formatted_log = {
        'Timestamp': log[0],
        'LogLevel': log[1],
        'Message': log[2]
    }
    formatted_logs.append(formatted_log)

# Convert logs to JSON
logs_json = json.dumps(formatted_logs)

# Set headers for API request
headers = {
    'Content-Type': 'application/json',
    'Log-Type': 'ApplicationLogs',
    'x-ms-date': '2022-04-06T11:11:11Z',
    'Authorization': f'SharedKey {workspace_id}:{workspace_key}'
}

# Send logs to Log Analytics workspace
response = requests.post(api_endpoint, data=logs_json, headers=headers)

# Check response status
if response.status_code == 200:
    print('Logs successfully sent to Log Analytics workspace.')
else:
    print(f'Failed to send logs. Status code: {response.status_code}, Response text: {response.text}')