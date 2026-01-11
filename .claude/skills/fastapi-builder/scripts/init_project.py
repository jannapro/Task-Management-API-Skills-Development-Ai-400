#!/usr/bin/env python3
"""
Initialize a new FastAPI project from a template.

Usage:
    python scripts/init_project.py <project_name> <template> [--path <output_path>]

Templates:
    hello-world      - Basic FastAPI starter
    intermediate-api - API with database integration and proper structure
    production-ready - Full-featured with auth, testing, and deployment configs

Examples:
    python scripts/init_project.py myapp hello-world
    python scripts/init_project.py myapi intermediate-api --path /path/to/projects
    python scripts/init_project.py prodapp production-ready
"""

import argparse
import os
import shutil
from pathlib import Path


TEMPLATES = {
    "hello-world": "Basic FastAPI starter",
    "intermediate-api": "API with database integration",
    "production-ready": "Full-featured production app"
}


def init_project(project_name: str, template: str, output_path: str = "."):
    """
    Initialize a new FastAPI project from a template.

    Args:
        project_name: Name of the new project
        template: Template to use (hello-world, intermediate-api, production-ready)
        output_path: Directory where the project will be created
    """
    # Validate template
    if template not in TEMPLATES:
        print(f"❌ Invalid template: {template}")
        print(f"   Available templates: {', '.join(TEMPLATES.keys())}")
        return False

    # Get template path
    script_dir = Path(__file__).parent
    skill_dir = script_dir.parent
    template_path = skill_dir / "assets" / template

    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        return False

    # Create output path
    output_dir = Path(output_path) / project_name

    if output_dir.exists():
        print(f"❌ Directory already exists: {output_dir}")
        return False

    # Copy template
    try:
        print(f"🚀 Creating FastAPI project: {project_name}")
        print(f"   Template: {template} - {TEMPLATES[template]}")
        print(f"   Location: {output_dir}")
        print()

        shutil.copytree(template_path, output_dir)

        print("✅ Project created successfully!")
        print()
        print("Next steps:")
        print(f"   1. cd {project_name}")
        print(f"   2. python -m venv venv")
        print(f"   3. source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        print(f"   4. pip install -r requirements.txt")

        if template == "production-ready":
            print(f"   5. cp .env.example .env")
            print(f"   6. Edit .env and set your SECRET_KEY")
            print(f"   7. fastapi dev main.py")
        else:
            print(f"   5. fastapi dev main.py")

        print()
        print(f"   API will be available at http://127.0.0.1:8000")
        print(f"   Docs will be available at http://127.0.0.1:8000/docs")

        return True

    except Exception as e:
        print(f"❌ Error creating project: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new FastAPI project from a template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "project_name",
        help="Name of the new project"
    )

    parser.add_argument(
        "template",
        choices=list(TEMPLATES.keys()),
        help="Template to use"
    )

    parser.add_argument(
        "--path",
        default=".",
        help="Output directory (default: current directory)"
    )

    args = parser.parse_args()

    success = init_project(args.project_name, args.template, args.path)
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
