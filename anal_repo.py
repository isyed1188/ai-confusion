import os
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "codellama:13b"

# Define allowed file extensions
VALID_EXTENSIONS = {".py", ".sh", ".bash", ".yml", ".yaml", ".json", ".toml", ".ini", ".md"}

def get_all_code_files(repo_path):
    """Recursively get all relevant code and config files."""
    code_files = []
    for root, _, files in os.walk(repo_path):
        if ".git" in root or "node_modules" in root:  # Skip irrelevant directories
            continue
        for file in files:
            if any(file.endswith(ext) for ext in VALID_EXTENSIONS):
                code_files.append(os.path.join(root, file))
    return code_files

def read_file(file_path):
    """Read a file and return its content, handling large files safely."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            if len(content) > 5000:  # Truncate large files
                return content[:5000] + "\n\n# [Truncated for length]"
            return content
    except Exception as e:
        return f"Error reading {file_path}: {e}"

def query_ollama(prompt):
    """Send a prompt to the local Ollama server."""
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "max_tokens": 500,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json().get("response", "No response received.")
    except requests.exceptions.RequestException as e:
        return f"Error querying Ollama: {e}"

if __name__ == "__main__":
    repo_path = input("Enter the path to your repo: ").strip()
    files = get_all_code_files(repo_path)

    print(f"Found {len(files)} relevant files. Sending to Ollama...\n")

    for file_path in files:
        file_content = read_file(file_path)
        prompt = f"Analyze the following file ({file_path}) and provide feedback:\n\n{file_content}"
        response = query_ollama(prompt)
        
        print(f"\n### Analysis of {file_path} ###")
        print(response)
        print("-" * 80)
