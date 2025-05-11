import os

# OpenAI API Key (if you plan to use OpenAI)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Ollama URL
# Default to localhost, but will be updated from user input
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")

# Default Models
DEFAULT_OLLAMA_MODEL = "llama3:latest"  # Or any other model you have pulled
DEFAULT_OPENAI_MODEL = "gpt-3.5-turbo" # Or any other OpenAI model