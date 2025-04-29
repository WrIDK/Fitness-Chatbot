 # ollama_api.py
import requests
import json

def stream_ollama(prompt, model="mistral"):
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }
    try:
        with requests.post(url, headers=headers, json=payload, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        if "response" in data:
                            yield data["response"]
                    except json.JSONDecodeError:
                        continue  # Skip bad lines
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Ollama: {e}")
        yield "Error: Couldn't connect to AI model."
