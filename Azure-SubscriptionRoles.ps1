Import-Module Az -Force -Verbose

Connect-AzAccount

#Get current date and set it to a variable
$CurrentDate = Get-Date -Format "yyyy.MM.dd"

# Get all Azure subscriptions
$AllSubscriptions = Get-AzSubscription

# Define the SubscriptionIds array dynamically
$SubIDs = $AllSubscriptions.Id

# Initialize the RoleAssignments array
$RoleAssignments = @()

foreach ($subscriptionId in $SubIDs) {
    Set-AzContext -Subscription $subscriptionId
    $currentsubscription = Get-AzSubscription -SubscriptionId $subscriptionId
    $currentRoleAssignments = Get-AzRoleAssignment | Select-Object Scope, RoleDefinitionName, DisplayName, `
                              @{Name="SubscriptionName"; Expression={$currentSubscription.Name}}
    $RoleAssignments += $currentRoleAssignments
}

# Output the role assignments to CSV
$RoleAssignments | Export-Csv -Path "C:\Users\BrettBauer\Access Controls\2024\$CurrentDate.AzureSubscriptionRoles.csv" -NoTypeInformation

 