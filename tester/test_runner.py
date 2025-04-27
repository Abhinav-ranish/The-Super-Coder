# tester/test_runner.py

import subprocess
import os
import sys
from tester.input_feeder import count_inputs_and_prompts, generate_fake_inputs


def install_requirements(base_path: str):
    """
    Install dependencies from requirements.txt if it exists.
    Skips known standard libraries.
    """
    requirements_path = os.path.join(base_path, "requirements.txt")
    if os.path.exists(requirements_path):
        print("📦 Installing dependencies from requirements.txt...")
        try:
            with open(requirements_path, "r") as f:
                packages = [line.strip() for line in f if line.strip()]
            
            # List of standard libraries to skip
            standard_libs = {"math", "sys", "os", "json", "re", "datetime", "time", "random", "typing", "subprocess"}

            install_packages = [pkg for pkg in packages if pkg.split("==")[0] not in standard_libs]

            if install_packages:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install"] + install_packages,
                    cwd=base_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=120
                )
                if result.returncode == 0:
                    print("✅ Dependencies installed successfully.")
                else:
                    print("❌ Failed to install dependencies.")
                    print(result.stderr.decode())
            else:
                print("ℹ️ No external dependencies to install.")

        except Exception as e:
            print(f"❌ Error installing dependencies: {e}")
    else:
        print("ℹ️ No requirements.txt found. Skipping dependency installation.")


def run_python_app(base_path: str) -> (bool, str):
    """
    Try running a Python app to check if it works.
    Returns (success: bool, error_message: str).
    """

    # Step 1: Install dependencies automatically first
    install_requirements(base_path)

    # Step 2: Find main .py file
    app_files = [f for f in os.listdir(base_path) if f.endswith('.py')]

    if not app_files:
        return False, "No Python app file found."

    main_file = None
    for file in app_files:
        if file == "app.py":
            main_file = file
            break
    if not main_file:
        main_file = app_files[0]

    main_file_path = os.path.join(base_path, main_file)

    # Step 3: Detect if app expects user input
    with open(main_file_path, "r", encoding="utf-8") as f:
        code_content = f.read()
        prompts = count_inputs_and_prompts(code_content)

    if prompts:
        print(f"ℹ️ Detected {len(prompts)} input() calls. Preparing to generate inputs...")
        fake_input_data = generate_fake_inputs(prompts)
        print(f"📝 Using generated fake input:\n{fake_input_data}\n")
    else:
        fake_input_data = None


    # Step 4: Try running the app
    try:
        if fake_input_data:
            result = subprocess.run(
                [sys.executable, main_file],
                cwd=base_path,
                input=fake_input_data.encode('utf-8'),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=20
            )
        else:
            result = subprocess.run(
                [sys.executable, main_file],
                cwd=base_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=15
            )

        if result.returncode == 0:
            return True, "App ran successfully."
        else:
            return False, result.stderr.decode()

    except subprocess.TimeoutExpired:
        return False, "App timed out. Possible infinite loop or wrong input."
    except Exception as e:
        return False, str(e)
