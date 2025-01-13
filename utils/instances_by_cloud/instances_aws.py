import boto3
from concurrent.futures import ThreadPoolExecutor

def get_instance_specs_and_availability():
    ec2 = boto3.client('ec2')
    
    # Get all instance types
    response = ec2.describe_instance_types()
    instance_types = response['InstanceTypes']
    
    # Get availability by region
    regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]
    
    instance_data = {}

    def check_region(instance_type, region):
        ec2_region = boto3.client('ec2', region_name=region)
        offerings = ec2_region.describe_instance_type_offerings(
            LocationType='region',
            Filters=[{'Name': 'instance-type', 'Values': [instance_type]}]
        )
        return region if offerings['InstanceTypeOfferings'] else None

    for instance in instance_types:
        instance_type = instance['InstanceType']
        specs = {
            'vCPU': instance['VCpuInfo']['DefaultVCpus'],
            'MemoryMiB': instance['MemoryInfo']['SizeInMiB'],
            'AvailableRegions': []
        }
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(check_region, instance_type, region) for region in regions]
            for future in futures:
                region = future.result()
                if region:
                    specs['AvailableRegions'].append(region)
        
        instance_data[instance_type] = specs
    
    return instance_data

# Call the function to get instance data
instance_data = get_instance_specs_and_availability()
print(instance_data)