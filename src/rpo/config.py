import json
from pathlib import Path

CONFIG_FILE = Path.home() / ".research_organiser_config.json"


def load_config():
    if not CONFIG_FILE.exists():
        return None
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(db_path, pdf_dir):
    config = {
        "db_path": str(Path(db_path).resolve()),
        "pdf_dir": str(Path(pdf_dir).resolve()),
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def get_config():
    config = load_config()
    if config is None:
        print("Configuration not found. Please set up the configuration first.")
        db_path = input("Enter the path for the database file: ")
        pdf_dir = input("Enter the directory for storing PDFs: ")
        save_config(db_path, pdf_dir)
        config = load_config()
    return config


def update_config():
    print("Updating configuration:")
    db_path = input(
        "Enter the new path for the database file (leave blank to keep current): "
    )
    pdf_dir = input(
        "Enter the new directory for storing PDFs (leave blank to keep current): "
    )

    current_config = load_config() or {}
    if db_path:
        current_config["db_path"] = str(Path(db_path).resolve())
    if pdf_dir:
        current_config["pdf_dir"] = str(Path(pdf_dir).resolve())

    save_config(current_config["db_path"], current_config["pdf_dir"])
    print("Configuration updated successfully.")
