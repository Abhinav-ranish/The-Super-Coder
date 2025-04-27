# main.py

import sys
import os
import json
from config import AI_ENGINE
from fixer.error_scraper import extract_error_details, prepare_initial_fix_prompt, check_if_more_files_needed, load_file_content
from fixer.smart_patcher import patch_file
from engines.ollama_engine import generate_response as ollama_response
from tester.test_runner import run_python_app
from generator.app_generator import create_project_structure

# Base system prompt
BASE_SYSTEM_PROMPT = """
You are a professional coding AI. Your task is to create full apps based on user ideas.

You must ONLY return a JSON object with the following format:
{
  "filename1.ext": "file content 1",
  "filename2.ext": "file content 2",
  ...
}

STRICT RULES:
- Every file MUST have a correct extension (.py, .html, .css, .js, etc.).
- For Python apps, you MUST include a 'requirements.txt' file listing only real pip packages (one per line, no comments).
- You MUST use only standard escaped JSON strings.
- You MUST NOT use triple quotes (avoid multi-line strings with triple quotes). Instead, represent multi-line text by escaping newlines using "\\n".
- NEVER use Markdown code block formatting (no ```python ```).
- NO explanations, no greetings, no extra text outside the JSON object.
- ONLY output pure machine-readable JSON.

⚠️ Reminder: Represent multi-line file contents using "\\n" inside strings, without triple quotes.
"""



def main():
    # CLI Mode
    if len(sys.argv) >= 3:
        user_prompt = sys.argv[1]
        stream_input = sys.argv[2]
        project_name = sys.argv[3]
        stream_mode = stream_input.lower() in ['y', 'yes', 'true', '1']
    else:
        # Interactive mode
        print("✨ Welcome to VibeCode Machine ✨")
        user_prompt = input("Describe the app you want to build: ")
        stream_mode = input("Do you want to stream the response? (y/n): ").lower().strip() == 'y'
        project_name = input("\n🗂️  What should be the project folder name?: ").strip()

    print("\n🧠 Thinking...\n")

    full_prompt = BASE_SYSTEM_PROMPT.strip() + "\n\nUser request:\n" + user_prompt

    # AI response
    if AI_ENGINE == "ollama":
        ai_response = ollama_response(full_prompt, stream=stream_mode)
    elif AI_ENGINE == "gemini":
        print("🔧 Gemini Engine - Coming soon!")
        ai_response = ""
    elif AI_ENGINE == "chatgpt":
        print("🔧 ChatGPT Engine - Coming soon!")
        ai_response = ""
    else:
        print("❌ Invalid AI_ENGINE setting.")
        return

    if not stream_mode and ai_response:
        print("✅ AI Response:")
        print(ai_response)

    if ai_response:
        try:
            project_structure = json.loads(ai_response)
            base_path = os.path.join(os.getcwd(), project_name)
            create_project_structure(base_path, project_structure)
        except json.JSONDecodeError:
            print("❌ AI response is not valid JSON format.")
            print("Hint: We need to ensure the AI follows JSON format strictly.")
            return

    # Testing app
    print("\n🛠️  Running app test...")
    success, message = run_python_app(base_path)

    if success:
        print("✅ App ran successfully!")
    else:
        print("❌ App failed to run.")
        print("Error:")
        print(message)

        # Auto-Fix if error
        print("\n🧠 Attempting to auto-fix...")

        error_message, crashed_filename = extract_error_details(message)

        if not crashed_filename:
            print("❌ Could not determine crashed file from error. Cannot auto-fix.")
            return

        crashed_file_content = load_file_content(base_path, crashed_filename)

        if not crashed_file_content:
            print(f"❌ Could not load {crashed_filename}. Cannot auto-fix.")
            return

        # Prepare Fix Prompt
        fix_prompt = prepare_initial_fix_prompt(error_message, crashed_filename, crashed_file_content)

        ai_response = ollama_response(fix_prompt, stream=False)

        extra_files_requested = check_if_more_files_needed(ai_response)

        retry_limit = 3
        retries = 0

        while extra_files_requested and retries < retry_limit:
            retries += 1
            for extra_file in extra_files_requested:
                extra_content = load_file_content(base_path, extra_file)
                if extra_content:
                    fix_prompt += f"\n\nAdditional file {extra_file}:\n```python\n{extra_content}\n```"
                else:
                    fix_prompt += f"\n\n⚠️ Warning: File {extra_file} not found."

            ai_response = ollama_response(fix_prompt, stream=False)
            extra_files_requested = check_if_more_files_needed(ai_response)

        print(f"🛠️  Applying AI Patch to {crashed_filename}...")
        patch_file(base_path, crashed_filename, ai_response)

        print("\n🛠️  Re-running app after auto-fix...")
        success, message = run_python_app(base_path)

        if success:
            print("✅ App ran successfully after auto-fix!")
        else:
            print("❌ App still failing after auto-fix.")
            print("New Error:")
            print(message)

if __name__ == "__main__":
    main()
