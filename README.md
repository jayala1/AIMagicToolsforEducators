# AIMagicToolsforEducators
An AI-powered, education-focused toolkit built with Flask. This web app integrates local inference via Ollama and cloud-based inference via OpenAI to offer a customizable interface for teachers, educators, and creators. In

🧪 Local Setup Instructions
Follow these steps to get the Open Source Magic Tools app up and running locally:

🔧 Prerequisites
Python 3.8 or newer

Pip (included with Python)

Git

Optional: A local Ollama model server (for offline use)

📦 Step 1: Clone the Repository\
git clone repository\
cd into the folder

🧰 Step 2: Create a Virtual Environment
python -m venv env

▶️ Step 3: Activate the Environment
On Windows (PowerShell):
env\Scripts\Activate
You should see (env) appear in your terminal prompt.

⚙️ Step 4: Set Environment Variables
Set up your inference backends via environment variables:\
$env:FLASK_APP = "open_source_magic_tools"\
$env:OPENAI_API_KEY = "your_openai_api_key"\
$env:OLLAMA_URL = "http://localhost:11434"\
You can skip OPENAI_API_KEY if only using Ollama.\

🚀 Step 5: Install Required Libraries
If you don’t yet have a requirements.txt, install manually:\
pip install Flask openai requests\
Or, if one is provided:\
pip install -r requirements.txt

🏃 Step 6: Run the Application
flask run
Then open http://127.0.0.1:5000 in your browser.

🔄 Optional: Regenerate Ollama Models
If using Ollama, click Save Settings and Fetch Models on the home page to populate your model list.
