# import boto3
# from azure.identity import DefaultAzureCredential
# from azure.mgmt.compute import ComputeManagementClient
# from google.cloud import compute_v1

# def get_aws_instances():
#     ec2 = boto3.client('ec2')
#     response = ec2.describe_instance_types()
#     return [instance['InstanceType'] for instance in response['InstanceTypes']]

# def get_azure_instances():
#     credential = DefaultAzureCredential()
#     compute_client = ComputeManagementClient(credential, "9591eed5-316a-4f40-8ea2-430e161ee367")
#     vm_sizes = compute_client.virtual_machine_sizes.list(location='eastus')
#     return [size.name for size in vm_sizes]

# def get_gcp_instances():
#     client = compute_v1.InstanceTypesClient()
#     request = compute_v1.ListInstanceTypesRequest(
#         project='mage-test-1234',
#         zone='us-central1-a'
#     )
#     instance_types = client.list(request=request)
#     return [instance.name for instance in instance_types]

# # Call the functions to get instance lists
# aws_instances = get_aws_instances()
# print("AWS Instances:", aws_instances)
# azure_instances = get_azure_instances()
# print("Azure Instances:", azure_instances)
# gcp_instances = get_gcp_instances()



# print("GCP Instances:", gcp_instances)

import boto3
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from google.cloud import compute_v1
from concurrent.futures import ThreadPoolExecutor
import csv

def get_aws_instances():
    ec2 = boto3.client('ec2')
    response = ec2.describe_instance_types()
    instances = []
    for instance in response['InstanceTypes']:
        instances.append({
            'name': instance['InstanceType'],
            'vCPU': instance['VCpuInfo']['DefaultVCpus'],
            'MemoryMiB': instance['MemoryInfo']['SizeInMiB']
        })
    return instances

def get_azure_instances():
    credential = DefaultAzureCredential()
    compute_client = ComputeManagementClient(credential, "9591eed5-316a-4f40-8ea2-430e161ee367")
    vm_sizes = compute_client.virtual_machine_sizes.list(location='eastus')
    instances = []
    for size in vm_sizes:
        instances.append({
            'name': size.name,
            'vCPU': size.number_of_cores,
            'MemoryMiB': size.memory_in_mb
        })
    return instances

def get_gcp_instances():
    client = compute_v1.MachineTypesClient()
    request = compute_v1.ListMachineTypesRequest(
        project='mage-test-1234',
        zone='us-central1-a'
    )
    instance_types = client.list(request=request)
    instances = []
    for instance in instance_types:
        instances.append({
            'name': instance.name,
            'vCPU': instance.guest_cpus,
            'MemoryMiB': instance.memory_mb
        })
    return instances

def save_instances_to_csv(instances, filename):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Cloud', 'Name', 'vCPU', 'MemoryMiB']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for cloud, cloud_instances in instances.items():
            for instance in cloud_instances:
                writer.writerow({
                    'Cloud': cloud,
                    'Name': instance['name'],
                    'vCPU': instance['vCPU'],
                    'MemoryMiB': instance['MemoryMiB']
                })

# Call the functions to get instance lists
aws_instances = get_aws_instances()
azure_instances = get_azure_instances()
gcp_instances = get_gcp_instances()

# Combine all instances into a dictionary
all_instances = {
    'AWS': aws_instances,
    'Azure': azure_instances,
    'GCP': gcp_instances
}

# Save the instances to a CSV file
save_instances_to_csv(all_instances, 'cloud_instances.csv')