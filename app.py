import gradio as gr
import requests
import json
import pandas as pd
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class CloudInstance:
    cloud: str
    name: str
    vcpu: int
    memory_mib: int

def load_instances(csv_path: str) -> List[CloudInstance]:
    """Load cloud instances from CSV file."""
    df = pd.read_csv(csv_path)
    instances = []
    for _, row in df.iterrows():
        instances.append(CloudInstance(
            cloud=row['Cloud'],
            name=row['Name'],
            vcpu=row['vCPU'],
            memory_mib=row['MemoryMiB']
        ))
    return instances

def fetch_model_info(model_name: str) -> Dict:
    """Fetch model information from HuggingFace API using authentication."""
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    hf_token = os.getenv('HUGGING_FACE_TOKEN')
    
    if not hf_token:
        raise Exception("HUGGING_FACE_TOKEN not found in .env file")
    
    headers = {"Authorization": f"Bearer {hf_token}"}
    api_url = f"https://huggingface.co/api/models/{model_name}"
    
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching model info: {str(e)}")

import re

def estimate_model_requirements(model_info: Dict) -> Tuple[int, int]:
    """
    Estimate model requirements:
    - Number of vCPUs needed
    - Memory needed in MiB
    Returns: (vcpu_count, memory_mib)
    """
    params_billion = None

    # Method 1: Check if size is provided directly
    if "size" in model_info:
        params_billion = float(model_info["size"])

    # Method 2: Check if size is in model name
    if params_billion is None and "modelId" in model_info:
        model_name = model_info["modelId"].lower()
        
        # Look for patterns like "70b", "7b", "13b", etc.
        size_patterns = [
            r'[^a-zA-Z](\d+)b[^a-zA-Z]',  # matches " 70b ", "-70b-", etc.
            r'[^a-zA-Z](\d+)b'            # matches "70b" at end of string
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, model_name)
            if match:
                params_billion = float(match.group(1))
                break
    
    # Method 3: Try to find size in model description or tags
    if params_billion is None and "description" in model_info:
        desc = model_info["description"].lower()
        matches = re.findall(r'(\d+)\s*[bb]illion parameters', desc)
        if matches:
            params_billion = float(matches[0])
    
    if params_billion is None:
        raise Exception("Could not determine model size. Please provide size manually or check model name format.")
    
    # Estimate requirements based on model size
    # These are rough estimates and can be tuned based on real-world data
    memory_per_billion_params = 4 * 1024  # About 4GB per billion parameters
    memory_mib = int(params_billion * memory_per_billion_params)
    
    # Estimate vCPU requirements
    # Rough estimate: 1 vCPU per 2B parameters, minimum 2 vCPUs
    vcpu_count = max(2, int(params_billion / 2))
    
    return vcpu_count, memory_mib

def recommend_instances(
    instances: List[CloudInstance],
    required_vcpu: int,
    required_memory_mib: int,
    max_recommendations: int = 2
) -> Dict[str, List[CloudInstance]]:
    """Find suitable cloud instances based on requirements."""
    recommendations = {}
    clouds = set(inst.cloud for inst in instances)
    
    for cloud in clouds:
        cloud_instances = [
            inst for inst in instances
            if inst.cloud == cloud and inst.vcpu >= required_vcpu and inst.memory_mib >= required_memory_mib
        ]
        
        if not cloud_instances:
            recommendations[cloud] = []
            continue
        
        # Sort by resource efficiency (trying to minimize over-provisioning)
        def score_instance(instance: CloudInstance) -> float:
            cpu_ratio = instance.vcpu / required_vcpu
            mem_ratio = instance.memory_mib / required_memory_mib
            # Lower score is better - we want resources as close to requirements as possible
            return abs(1 - cpu_ratio) + abs(1 - mem_ratio)
        
        cloud_instances.sort(key=score_instance)
        recommendations[cloud] = cloud_instances[:max_recommendations]
    
    return recommendations

def format_recommendation(instance: CloudInstance) -> str:
    """Format instance details for display."""
    return (
        f"Provider: {instance.cloud}\n"
        f"Instance: {instance.name}\n"
        f"vCPUs: {instance.vcpu}\n"
        f"Memory: {instance.memory_mib / 1024:.1f} GiB"
    )

def get_recommendations(model_name: str) -> Tuple[str, str, str]:
    """Main function to get cloud instance recommendations."""
    try:
        # Load instances
        instances = load_instances('cloud_instances.csv')
        
        # Fetch model information
        model_info = fetch_model_info(model_name)
        required_vcpu, required_memory = estimate_model_requirements(model_info)
        
        # Get recommendations
        recommendations = recommend_instances(instances, required_vcpu, required_memory)
        
        # Prepare output
        model_details = (
            f"Model: {model_name}\n"
            f"Estimated requirements:\n"
            f"- vCPUs: {required_vcpu}\n"
            f"- Memory: {required_memory / 1024:.1f} GiB"
        )
        
        primary_rec = ""
        backup_rec = ""
        
        for cloud, recs in recommendations.items():
            if recs:
                primary_rec += f"\n\n{cloud} Primary Recommendation:\n" + format_recommendation(recs[0])
                if len(recs) > 1:
                    backup_rec += f"\n\n{cloud} Backup Recommendation:\n" + format_recommendation(recs[1])
                else:
                    backup_rec += f"\n\n{cloud} Backup Recommendation: No backup recommendation available"
            else:
                primary_rec += f"\n\n{cloud} Primary Recommendation: No suitable instances found"
                backup_rec += f"\n\n{cloud} Backup Recommendation: No suitable instances found"
        
        return model_details, primary_rec.strip(), backup_rec.strip()
    
    except Exception as e:
        return f"Error: {str(e)}", "", ""

# Create Gradio interface
with gr.Blocks() as app:
    gr.Markdown("# INstaMatch as i Cloud Instance Matching for ML Models")
    gr.Markdown("Enter a model name from HuggingFace to get cloud instance recommendations")
    
    with gr.Row():
        model_input = gr.Textbox(
            label="Model Name (e.g., gpt2, bert-base-uncased)",
            placeholder="Enter model name..."
        )
        submit_btn = gr.Button("Get Recommendations")
    
    with gr.Row():
        model_info = gr.Textbox(label="Model Requirements", lines=4)
        primary_rec = gr.Textbox(label="Primary Recommendation", lines=5)
        backup_rec = gr.Textbox(label="Backup Recommendation", lines=5)
    
    submit_btn.click(
        fn=get_recommendations,
        inputs=model_input,
        outputs=[model_info, primary_rec, backup_rec]
    )

if __name__ == "__main__":
    app.launch()