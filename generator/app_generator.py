# generator/app_generator.py

import os

def create_project_structure(base_path: str, files: dict):
    """
    Recursively create project folders and files from a dictionary structure.
    
    Args:
        base_path (str): Path where project should be created.
        files (dict): A dictionary {filename_or_folder: filecontent_or_subfolder}.
    """
    os.makedirs(base_path, exist_ok=True)

    for name, content in files.items():
        full_path = os.path.join(base_path, name)

        if isinstance(content, dict):
            # It's a subfolder, recurse
            create_project_structure(full_path, content)
        elif isinstance(content, str):
            # It's a file, create and write
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            print(f"⚠️ Unexpected content type for {name}: {type(content)}")

    print(f"✅ Project created at {base_path}")
