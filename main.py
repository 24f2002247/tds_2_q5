
import os
from pathlib import Path

import yaml
from dotenv import dotenv_values
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

def to_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {
        "true", "1", "yes", "on"
    }

def effective_config(overrides):
    config = DEFAULTS.copy()

    yaml_path = Path("config.development.yaml")
    if yaml_path.exists():
        with yaml_path.open() as f:
            config.update(yaml.safe_load(f) or {})

    env_file = dotenv_values(".env")
    if env_file.get("NUM_WORKERS") is not None:
        config["workers"] = env_file["NUM_WORKERS"]

    for key, value in os.environ.items():
        if key.startswith("APP_"):
            name = key[4:].lower()
            if name in config:
                config[name] = value

    for key, value in overrides:
        if key in config:
            config[key] = value

    config["port"] = int(config["port"])
    config["workers"] = int(config["workers"])
    config["debug"] = to_bool(config["debug"])
    config["log_level"] = str(config["log_level"])
    config["api_key"] = "****"

    return config

@app.get("/effective-config")
def get_config(
    set: list[str] = Query(default=[])
):
    overrides = []
    for item in set:
        if "=" in item:
            key, value = item.split("=", 1)
            overrides.append((key, value))

    return effective_config(overrides)
