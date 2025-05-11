import ollama
import openai
from .config import OPENAI_API_KEY, DEFAULT_OLLAMA_MODEL, DEFAULT_OPENAI_MODEL
from flask import current_app
import requests

# Configure OpenAI API (only if API key is provided)
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

def generate_text(prompt, model_type, model_name=None):
    try:
        if model_type == 'ollama':
            model_to_use = model_name if model_name else DEFAULT_OLLAMA_MODEL
            ollama_host = current_app.config.get('OLLAMA_URL', 'http://localhost:11434')
            client = ollama.Client(host=ollama_host)
            response = client.chat(model=model_to_use, messages=[{'role': 'user', 'content': prompt}])
            return response['message']['content']
        elif model_type == 'openai' and OPENAI_API_KEY:
            model_to_use = model_name if model_name else DEFAULT_OPENAI_MODEL
            response = openai.ChatCompletion.create(
                model=model_to_use,
                messages=[{'role': 'user', 'content': prompt}]
            )
            return response.choices[0].message['content']
        else:
            return "Please select an inference server."
    except Exception as e:
        print(f"Error interacting with inference server: {e}")
        return "An error occurred while generating the response."

def list_ollama_models():
    ollama_host = current_app.config.get('OLLAMA_URL', 'http://localhost:11434')
    print(f"Attempting to list Ollama models from: {ollama_host}")
    try:
        client = ollama.Client(host=ollama_host)
        models_response = client.list()
        print(f"Successfully received Ollama models response: {models_response}")

        # Check if 'models' key exists and is a list
        if 'models' in models_response and isinstance(models_response['models'], list):
            model_names = []
            for model in models_response['models']:
                # Access the 'model' attribute of the Model object
                if hasattr(model, 'model'):
                     model_names.append(model.model)
                else:
                    print(f"Warning: Unexpected model structure in Ollama response: {model}")
            print(f"Successfully extracted model names: {model_names}")
            return model_names
        else:
            print(f"Error: Ollama response does not contain expected 'models' list: {models_response}")
            return []

    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error listing Ollama models from {ollama_host}: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred listing Ollama models from {ollama_host}: {e}")
        return []