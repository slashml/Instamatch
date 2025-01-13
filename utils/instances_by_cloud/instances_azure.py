from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.subscription import SubscriptionClient

def get_azure_instances():
    credential = DefaultAzureCredential()
    subscription_client = SubscriptionClient(credential)
    subscription_id = next(subscription_client.subscriptions.list()).subscription_id
    compute_client = ComputeManagementClient(credential, subscription_id)

    instances = []
    locations = [location.name for location in compute_client.locations.list()]

    for location in locations:
        vm_sizes = compute_client.virtual_machine_sizes.list(location)
        for size in vm_sizes:
            instance_info = {
                'name': size.name,
                'vCPUs': size.number_of_cores,
                'memoryGB': size.memory_in_mb / 1024,
                'location': location
            }
            instances.append(instance_info)

    return instances

def save_instances_to_file(instances, filename):
    with open(filename, 'w') as file:
        for instance in instances:
            file.write(f"Name: {instance['name']}, vCPUs: {instance['vCPUs']}, Memory: {instance['memoryGB']} GB, Location: {instance['location']}\n")

azure_instances = get_azure_instances()
save_instances_to_file(azure_instances, 'azure_instances.txt')
