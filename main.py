import sys
import os
import json
import subprocess
from config import AI_ENGINE
from fixer.error_scraper import extract_error_details, prepare_initial_fix_prompt, check_if_more_files_needed, load_file_content
from fixer.smart_patcher import patch_file
from engines.ollama_engine import generate_response as ollama_response
from generator.app_generator import create_project_structure
from tester.test_runner import install_requirements

# Base system prompt with placeholders for language and run command
BASE_SYSTEM_PROMPT = """
You are a professional coding AI. Your task is to create full apps based on user ideas.

Project Language: {language}
Run Command: {run_cmd}

You must ONLY return a JSON object with the following format:
{{
  "filename1.ext": "file content 1",
  "filename2.ext": "file content 2",
  ...
}}

STRICT RULES:
- Every file MUST have a correct extension (.py, .html, .css, .js, etc.).
- For Python apps, you MUST include a 'requirements.txt' file listing only real pip packages (one per line, no comments).
- You MUST use only standard escaped JSON strings.
- You MUST NOT use triple quotes. Instead, represent multi-line text by escaping newlines using "\\n".
- NEVER use Markdown code block formatting.
- NO explanations, no greetings, no extra text outside the JSON object.
- ONLY output pure machine-readable JSON.

⚠️ Reminder: Represent multi-line file contents using "\\n" inside strings, without triple quotes.
"""


def run_command(base_path: str, command: str):
    """
    Executes the given shell command in the project directory.
    Returns (success: bool, output: str).
    """
    result = subprocess.run(command, shell=True, cwd=base_path, capture_output=True, text=True)
    return (result.returncode == 0, result.stdout + result.stderr)


def main():
    # CLI Mode expects: user_prompt, stream_flag, project_name, language
    if len(sys.argv) >= 5:
        user_prompt = sys.argv[1]
        stream_input = sys.argv[2]
        project_name = sys.argv[3]
        language = sys.argv[4]
        stream_mode = stream_input.lower() in ['y','yes','true','1']
    else:
        print("✨ Welcome to VibeCode Machine CLI ✨")
        user_prompt = input("Describe the app you want to build: ")
        language = input("Which programming language should be used? ").strip() or "Python"
        stream_mode = input("Do you want to stream the AI response? (y/n): ").lower().strip() in ['y','yes']
        project_name = input("What should be the project folder name?: ").strip()

    # Determine run command
    if language.lower().startswith("python"):
        run_cmd = "python main.py"
    else:
        print(f"🤖 Determining run command for {language}...")
        cmd_prompt = f"As a shell command, how would you run a project written in {language}? Respond with only the command."
        run_cmd = ollama_response(cmd_prompt, stream=False).strip().splitlines()[0]

    print("\n🧠 Thinking...\n")
    prompt_header = BASE_SYSTEM_PROMPT.format(language=language, run_cmd=run_cmd).strip()
    full_prompt = f"{prompt_header}\n\nUser request:\n{user_prompt}"

    # Generate project structure JSON
    if AI_ENGINE == "ollama":
        ai_response = ollama_response(full_prompt, stream=stream_mode)
    else:
        print(f"❌ AI_ENGINE '{AI_ENGINE}' not supported in CLI.")
        return

    if not stream_mode and ai_response:
        print("✅ AI Response:")
        print(ai_response)

    base_path = os.path.join(os.getcwd(), project_name)
    if ai_response:
        try:
            project_structure = json.loads(ai_response)
            create_project_structure(base_path, project_structure)
        except json.JSONDecodeError:
            print("❌ AI response is not valid JSON format.")
            return

    # Install dependencies via test_runner
    print("📦 Installing dependencies if any...")
    deps_success, deps_output = install_requirements(base_path)
    print(deps_output)
    if not deps_success:
        print("❌ Failed to install dependencies. Aborting.")
        return

    # Run the determined command
    print("\n🛠️  Running project command...")
    success, message = run_command(base_path, run_cmd)

    if success:
        print("✅ Project ran successfully!")
        return
    else:
        print("❌ Command failed with error:")
        print(message)

    # Auto-fix loop
    print("\n🧠 Attempting to auto-fix...\n")
    error_message, crashed_filename = extract_error_details(message)
    if not crashed_filename:
        print("❌ Could not determine crashed file from error.")
        return

    crashed_file_content = load_file_content(base_path, crashed_filename)
    if not crashed_file_content:
        print(f"❌ Could not load {crashed_filename}.")
        return

    fix_prompt = prepare_initial_fix_prompt(error_message, crashed_filename, crashed_file_content)
    fix_prompt += f"\nThe command used was: {run_cmd}\n"
    fix_prompt += "If the failure is due to a wrong command, respond with 'Command: <corrected command>'. "
    fix_prompt += "If the failure is due to code errors, respond with 'Change:' and provide the updated code snippet."

    ai_response = ollama_response(fix_prompt, stream=False)
    extra_files = check_if_more_files_needed(ai_response)
    retries = 0
    while extra_files and retries < 3:
        retries += 1
        for extra in extra_files:
            content = load_file_content(base_path, extra)
            if content:
                fix_prompt += f"\nAdditional file {extra}:\n```python\n{content}\n```"
        ai_response = ollama_response(fix_prompt, stream=False)
        extra_files = check_if_more_files_needed(ai_response)

    if ai_response.strip().startswith("Command:"):
        new_cmd = ai_response.split("Command:",1)[1].strip()
        print(f"🔄 Retrying with corrected command: {new_cmd}")
        success, message = run_command(base_path, new_cmd)
        if success:
            print("✅ Corrected command executed successfully!")
        else:
            print("❌ Corrected command still failed:")
            print(message)
    else:
        print(f"🛠️  Applying AI Patch to {crashed_filename}...")
        patch_file(base_path, crashed_filename, ai_response)
        print("\n🛠️  Re-running project command after auto-fix...")
        success, message = run_command(base_path, run_cmd)
        if success:
            print("✅ Project ran successfully after auto-fix!")
        else:
            print("❌ Still failing after auto-fix:")
            print(message)

if __name__ == "__main__":
    main()
