# fixer/smart_patcher.py

import re
import os

def parse_code_blocks(code: str):
    """
    Parses functions, classes, and imports from a Python file.
    Returns a dict {block_name: block_content}.
    """
    blocks = {}
    current_block = None
    current_content = []

    lines = code.splitlines()

    for line in lines:
        line_strip = line.strip()

        if line_strip.startswith("def ") or line_strip.startswith("class "):
            # Save previous block
            if current_block:
                blocks[current_block] = "\n".join(current_content)

            current_block = re.findall(r'(def|class)\s+(\w+)', line_strip)[0][1]
            current_content = [line]
        elif line_strip.startswith("import ") or line_strip.startswith("from "):
            # Treat imports as part of special "_imports" block
            blocks.setdefault("_imports", "")
            blocks["_imports"] += line + "\n"
        else:
            if current_block:
                current_content.append(line)

    if current_block:
        blocks[current_block] = "\n".join(current_content)

    return blocks

def generate_patch(old_code: str, new_code: str):
    """
    Compares old and new code blocks, and returns updated blocks.
    """
    old_blocks = parse_code_blocks(old_code)
    new_blocks = parse_code_blocks(new_code)

    patch_blocks = {}

    for block_name, new_content in new_blocks.items():
        if block_name not in old_blocks:
            # New function/class/import
            patch_blocks[block_name] = new_content
        elif old_blocks[block_name] != new_content:
            # Changed function/class
            patch_blocks[block_name] = new_content

    return patch_blocks

def apply_patch(base_code: str, patch_blocks: dict):
    """
    Applies updated blocks into the base code.
    """
    lines = base_code.splitlines()
    final_lines = []
    inside_block = False
    current_block_name = None

    for line in lines:
        line_strip = line.strip()

        # Check for block starts
        if line_strip.startswith("def ") or line_strip.startswith("class "):
            block_name = re.findall(r'(def|class)\s+(\w+)', line_strip)[0][1]
            if block_name in patch_blocks:
                # Replace this entire block
                final_lines.append(patch_blocks[block_name])
                inside_block = True
                current_block_name = block_name
                continue

        if inside_block:
            if line.startswith(" " * 4) or line == "":
                continue  # skip old block lines
            else:
                inside_block = False  # out of block

        if not inside_block:
            final_lines.append(line)

    # Add any new blocks that were not originally there
    for block_name, content in patch_blocks.items():
        if block_name not in base_code:
            final_lines.append(content)

    return "\n".join(final_lines)

def patch_file(base_path: str, filename: str, new_code: str):
    """
    Loads base file, applies patch, saves the new file.
    """
    file_path = os.path.join(base_path, filename)
    if not os.path.exists(file_path):
        print(f"❌ File {filename} not found for patching.")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        base_code = f.read()

    patch_blocks = generate_patch(base_code, new_code)
    updated_code = apply_patch(base_code, patch_blocks)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(updated_code)

    print(f"✅ Patched {filename} successfully.")
