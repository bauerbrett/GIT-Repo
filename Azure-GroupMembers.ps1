# Define the Azure AD tenant ID
$TenantId = ""

# Function to connect to Azure AD and set the tenant
function Connect-AzureADAndSetTenant {

    # Check if already connected to the correct tenant
    $currentContext = Get-AzureADTenantDetail | Where-Object { $_.ObjectId -eq $TenantId }
    if ($currentContext) {
        Write-output "Already connected to Azure AD tenant with ID: $TenantId"
    }
    else {

        # Connect to Azure AD
        Connect-AzureAD -TenantId $TenantId

        Write-Output "Connected to Azure AD tenant with ID: $TenantId"
    }
}

# Call the function to connect to Azure AD and set the tenant
Connect-AzureADAndSetTenant

# Get Azure AD groups from the specified tenant
$AllGroups = Get-AzureADGroup -All $true

# Filter groups from the specified tenant
$FilteredGroups = $AllGroups | Where-Object { $_.DisplayName -like "*$TenantId*" }

# Display the filtered groups
$FilteredGroups | Select-Object DisplayName, ObjectId, ObjectType
 
# Now you can proceed with your Azure AD operations
# Get current date and set it to a variable
$CurrentDate = Get-Date -Format "yyyy.MM.dd"

# Get all Azure AD Groups
$AllGroups = Get-AzureADGroup -All $true

# Pull the ObjectID out of $AllGroups
$GroupIDs = $AllGroups.ObjectId

# Make Group Assignment Array
$GroupAssignments = @()

# Loop to grab each group and run Azure AD commands
foreach ($GroupId in $GroupIds) {
    $group = Get-AzureADGroup -ObjectId $GroupId
    $members = Get-AzureADGroupMember -ObjectId $GroupId -All $true

    $GroupAndMembers = @{
        GroupDisplayName = $group.DisplayName
        GroupObjectId = $group.ObjectId
        GroupObjectType = $group.ObjectType
        Members = @()
    }

    foreach ($member in $members) {
        $MemberDetails = @{
            MemberDisplayName = $member.DisplayName
            MemberObjectId = $member.ObjectId
            MemberObjectType = $member.ObjectType
        }
        $GroupAndMembers.Members += New-Object PSObject -Property $MemberDetails
    }
    # Combine group assignment with group and members
    $GroupAssignments += New-Object PSObject -Property $GroupAndMembers

}

# Specify the path where you want to save the CSV file
$OutputFilePath = "C:\Users\BrettBauer\ Access Controls\2024\$CurrentDate.ADGroupMembers.csv"

# Select properties for CSV output and Export Data to CSV
$GroupAssignments | Select-Object GroupDisplayName, GroupObjectType, @{Name="MemberDisplayName"; Expression={$_.Members.MemberDisplayName -join ', '}} | Export-Csv -Path $OutputFilePath -NoTypeInformation