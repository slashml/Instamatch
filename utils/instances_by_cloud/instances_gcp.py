from google.cloud import compute_v1

def get_gcp_instances(project_id, zone):
    client = compute_v1.InstanceTypesClient()
    request = compute_v1.ListInstanceTypesRequest(
        project=project_id,
        zone=zone
    )
    instances = []
    for instance_type in client.list(request=request):
        instance_info = {
            'name': instance_type.name,
            'description': instance_type.description,
            'guestCpus': instance_type.guest_cpus,
            'memoryMb': instance_type.memory_mb
        }
        instances.append(instance_info)
    return instances

def get_gcp_zones(project_id):
    client = compute_v1.ZonesClient()
    request = compute_v1.ListZonesRequest(project=project_id)
    return [zone.name for zone in client.list(request=request)]
