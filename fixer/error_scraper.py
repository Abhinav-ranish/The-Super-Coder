# fixer/error_scraper.py

import re
import os

def extract_error_details(stderr_text: str):
    """
    Extracts error message and crashed filename from stderr output.
    Returns (error_message, filename) or (error_message, None) if not found.
    """
    # Try to find filename in the stack trace
    match = re.search(r'File \"(.*?)\", line (\d+)', stderr_text)
    if match:
        filename = os.path.basename(match.group(1))
    else:
        filename = None

    # Grab the last line of the error for the main message
    lines = stderr_text.strip().splitlines()
    error_message = lines[-1] if lines else "Unknown error"

    return error_message, filename

def prepare_initial_fix_prompt(error_message: str, filename: str, file_content: str):
    """
    Prepare the first prompt to AI for fixing the crash.
    """
    prompt = f"""
You are a senior software engineer.

The following app crashed.

Crash error:
{error_message}

Code in {filename}:
```python
{file_content}
```

Please analyze the code and suggest minimal corrections to fix the crash.

If you need to see any other files to understand better, just reply:
"Please show me [filename]".

Otherwise, please provide the fixed version of {filename}.
    """.strip()

    return prompt

def check_if_more_files_needed(ai_response: str):
    """
    Check AI response to see if it asks for more files.
    Returns a list of filenames it requests.
    """
    pattern = r'Please show me ([\w\.]+)'
    matches = re.findall(pattern, ai_response)

    return matches  # could be an empty list if no extra files requested

def load_file_content(base_path: str, filename: str):
    """
    Loads file content if it exists. Otherwise returns None.
    """
    file_path = os.path.join(base_path, filename)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return None
