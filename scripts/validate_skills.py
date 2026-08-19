import os
import re
import sys
import yaml

ALLOWED_KEYS = {"name", "description", "license", "allowed-tools", "metadata"}
NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
IGNORED_DIRS = {".git", ".github", "scripts", "__pycache__", "node_modules"}

def validate_yaml_file(filepath):
    """Ensure any standalone YAML file parses cleanly."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            yaml.safe_load(f)
        return True, None
    except Exception as e:
        return False, f"Invalid YAML syntax: {e}"

def validate_skill_file(skill_path):
    """Validate a single skill directory and its SKILL.md file."""
    skill_file = os.path.join(skill_path, "SKILL.md")
    errors = []

    if not os.path.isfile(skill_file):
        return [f"Missing required SKILL.md in {skill_path}"]

    try:
        with open(skill_file, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return [f"Cannot read {skill_file}: {e}"]

    # Check for frontmatter format: starts with --- and has closing ---
    if not content.startswith("---"):
        return [f"{skill_file}: Must start with YAML frontmatter delimiter '---'"]

    parts = content.split("---", 2)
    if len(parts) < 3:
        return [f"{skill_file}: Invalid YAML frontmatter structure (missing closing '---')"]

    frontmatter_raw = parts[1]

    try:
        data = yaml.safe_load(frontmatter_raw)
    except Exception as e:
        return [f"{skill_file}: YAML parse error in frontmatter: {e}"]

    if not isinstance(data, dict):
        return [f"{skill_file}: YAML frontmatter must be a key-value dictionary"]

    # Allowed keys
    unknown_keys = set(data.keys()) - ALLOWED_KEYS
    if unknown_keys:
        errors.append(f"{skill_file}: Disallowed frontmatter keys: {', '.join(sorted(unknown_keys))}")

    # Validate name
    name = data.get("name")
    if not name or not isinstance(name, str):
        errors.append(f"{skill_file}: 'name' is required and must be a string")
    else:
        if len(name) > 64:
            errors.append(f"{skill_file}: 'name' exceeds max length of 64 chars ({len(name)})")
        if not NAME_PATTERN.match(name):
            errors.append(f"{skill_file}: 'name' ('{name}') must be hyphen-case (lowercase alphanumeric with hyphens)")

    # Validate description
    description = data.get("description")
    if not description or not isinstance(description, str):
        errors.append(f"{skill_file}: 'description' is required and must be a string")
    else:
        if len(description) > 1024:
            errors.append(f"{skill_file}: 'description' exceeds max length of 1024 chars ({len(description)})")
        if "<" in description or ">" in description:
            errors.append(f"{skill_file}: 'description' must not contain '<' or '>' characters")

    # Validate any yaml files inside skill folder (e.g. agents/openai.yaml)
    for root, _, files in os.walk(skill_path):
        for file in files:
            if file.endswith((".yaml", ".yml")):
                full_yaml_path = os.path.join(root, file)
                valid, err = validate_yaml_file(full_yaml_path)
                if not valid:
                    errors.append(f"{full_yaml_path}: {err}")

    return errors

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    all_errors = []
    validated_skills = 0

    for item in sorted(os.listdir(root_dir)):
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path) and item not in IGNORED_DIRS:
            validated_skills += 1
            errs = validate_skill_file(item_path)
            if errs:
                all_errors.extend(errs)

    # Validate GitHub workflows if present
    workflow_dir = os.path.join(root_dir, ".github", "workflows")
    if os.path.isdir(workflow_dir):
        for file in os.listdir(workflow_dir):
            if file.endswith((".yaml", ".yml")):
                wf_path = os.path.join(workflow_dir, file)
                valid, err = validate_yaml_file(wf_path)
                if not valid:
                    all_errors.append(f"{wf_path}: {err}")

    print(f"Validated {validated_skills} skill(s).")

    if all_errors:
        print("\nValidation FAILED with errors:")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)

    print("All skills and YAML files passed validation.")
    sys.exit(0)

if __name__ == "__main__":
    main()
