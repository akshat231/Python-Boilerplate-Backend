# create_backend/cli.py
import shutil
import sys
from pathlib import Path

def main():
    # Check that a project name was passed
    if len(sys.argv) < 2:
        print("Usage: python create_backend/cli.py <project-name>")
        sys.exit(1)

    project_name = sys.argv[1]
    cwd = Path.cwd()
    target_dir = cwd / project_name

    if target_dir.exists():
        print(f"❌ Directory '{project_name}' already exists.")
        sys.exit(1)

    # Find the app folder relative to repo root
    repo_root = Path(__file__).resolve().parent.parent
    app_src = repo_root / "app"

    if not app_src.exists():
        print("❌ Could not find 'app/' folder in repo root.")
        sys.exit(1)

    # Copy the app folder into new project
    shutil.copytree(app_src, target_dir / "app")

    print(f"✅ Created new backend project '{project_name}' at {target_dir}")

# This ensures main() runs when the script is executed directly
if __name__ == "__main__":
    main()
