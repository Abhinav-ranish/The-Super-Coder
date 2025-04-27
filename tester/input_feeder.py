# tester/input_feeder.py

import re
from engines.ollama_engine import generate_response

def count_inputs_and_prompts(code_content: str):
    """
    Counts the number of input() calls and extracts their prompt texts.
    """
    pattern = r'input\s*\(\s*[\'"]?(.*?)[\'"]?\s*\)'
    matches = re.findall(pattern, code_content)
    return matches  # list of prompt texts

def generate_fake_inputs(prompt_list: list) -> str:
    """
    Uses AI to suggest fake input values for the given prompts.
    Returns a single string with \n-separated inputs.
    """
    if not prompt_list:
        return ""

    system_prompt = f"""
You are a coding assistant. Given the following prompts for input(), suggest realistic fake input values.

Only output the values the user would type, one per line. DO NOT repeat the prompt text. Only raw values separated by newline.

Prompts:
{chr(10).join(['- ' + p for p in prompt_list])}

Example:
5
8
42
    """.strip()

    fake_inputs = generate_response(system_prompt, stream=False)

    # Cleanup just in case
    return fake_inputs.strip()
