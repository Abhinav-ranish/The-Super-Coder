# engines/ollama_engine.py

import requests
from config import OLLAMA_MODEL, OLLAMA_BASE_URL

def generate_response(prompt: str, stream: bool = False) -> str:
    endpoint = f"{OLLAMA_BASE_URL}/api/chat"
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": stream
    }
    try:
        response = requests.post(endpoint, json=payload, stream=stream)
        response.raise_for_status()

        if stream:
            # Streaming response
            full_text = ""
            for line in response.iter_lines():
                if line:
                    line_data = line.decode('utf-8')
                    if line_data.startswith('data: '):
                        line_data = line_data[6:]
                    import json
                    content_piece = json.loads(line_data)
                    delta = content_piece.get('message', {}).get('content', '')
                    print(delta, end="", flush=True)  # typing effect
                    full_text += delta
            print("\n")  # After stream ends
            return full_text
        else:
            # Normal full response
            result = response.json()
            return result.get("message", {}).get("content", "")

    except Exception as e:
        print(f"Error communicating with Ollama: {e}")
        return ""
