import json
from pathlib import Path
from dataclasses import dataclass, asdict

CONFIG_FILE = Path.home() / ".rpo.json"
DB_FILE = Path.home() / ".research_papers.db"


@dataclass
class Config:
    db_str: str

    def __post_init__(self):
        self.db_path = Path(self.db_str).expanduser().resolve()


def load_config(db_file: Path = DB_FILE, config_file: Path = CONFIG_FILE) -> Config:
    if not config_file.exists():
        print(f"Using default configuration at: {str(CONFIG_FILE)}")
        config = Config(db_str=str(db_file.resolve()))
        save_config(config)
    with open(config_file, "r") as f:
        return Config(**json.load(f))


def save_config(config: Config, config_file: Path = CONFIG_FILE) -> None:
    with open(config_file, "w") as f:
        json.dump(asdict(config), f, indent=2)


def update_config() -> None:
    print("Updating configuration:")
    db_str = input(
        "Enter the new path for the database file (leave blank to keep current): "
    )
    if not db_str:
        print("Configuration not updated.")
        return
    config = load_config()
    config.db_str = db_str
    config.__post_init__()
    save_config(config)
    print("Configuration updated successfully.")
