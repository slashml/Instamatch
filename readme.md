## Overview
InstaMatch is a cloud instance matching tool for machine learning models. It fetches model information from HuggingFace and recommends suitable cloud instances from AWS, Azure, and GCP based on the model's requirements.

## Features
- Fetch model information from HuggingFace API
- Estimate model requirements (vCPUs and memory)
- Recommend suitable cloud instances from AWS, Azure, and GCP
- Display primary and backup recommendations

## Installation
1. Clone the repository:
   \`\`\`sh
   git clone https://github.com/yourusername/InstaMatch.git
   cd InstaMatch
   \`\`\`

2. Create and activate a virtual environment:
   \`\`\`sh
   python3 -m venv venv
   source venv/bin/activate
   \`\`\`

3. Install the required dependencies:
   \`\`\`sh
   pip install -r requirements.txt
   \`\`\`

4. Set up your HuggingFace API token in a \`.env\` file:
   \`\`\`sh
   echo \"HUGGING_FACE_TOKEN=your_huggingface_token\" > .env
   \`\`\`

## Usage
1. Run the application:
   \`\`\`sh
   python app.py
   \`\`\`

2. Open the provided URL in your browser.

3. Enter a model name from HuggingFace (e.g., \`gpt2\`, \`bert-base-uncased\`) and click \"Get Recommendations\".

4. View the model requirements and cloud instance recommendations.

## Files
- \`app.py\`: Main application file
- \`cloud_instances.csv\`: CSV file containing cloud instance data
- \`requirements.txt\`: List of required Python packages
- \`utils/\`: Utility functions and modules

## License
This project is licensed under the MIT License." > README.md

git add README.md
git commit -m "Add README file"