import os
from pathlib import Path
from typing import List, Optional

import yaml
from dotenv import dotenv_values
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

DEFAULTS = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

def as_bool(value):
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "on"}

def coerce(key, value):
    if key in {"port", "workers"}:
        return int(value)
    if key == "debug":
        return as_bool(value)
    return str(value)

def normalized_key(key):
    key = key.strip()
    if key.upper() == "NUM_WORKERS":
        return "workers"
    return key.lower()

def apply_layer(config, layer):
    for raw_key, value in layer.items():
        key = normalized_key(raw_key)
        if key in DEFAULTS and value is not None:
            config[key] = coerce(key, value)

def build_config(cli_sets: Optional[List[str]] = None):
    config = DEFAULTS.copy()

    env_name = os.getenv("APP_ENV", "development")
    yaml_path = Path(f"config.{env_name}.yaml")
    if yaml_path.exists():
        with yaml_path.open("r", encoding="utf-8") as f:
            apply_layer(config, yaml.safe_load(f) or {})

    # .env layer, deliberately below real OS environment variables.
    dotenv_layer = dotenv_values(".env")
    apply_layer(config, dotenv_layer)

    # OS-level APP_* variables override the file. Do not use os.environ
    # wholesale: only the required APP_* keys participate.
    os_layer = {}
    for env_key, value in os.environ.items():
        if env_key.startswith("APP_"):
            os_layer[env_key[4:].lower()] = value
    apply_layer(config, os_layer)

    # Query parameters are supplied as repeated set=key=value values.
    for item in (cli_sets or []):
        if "=" not in item:
            continue
        raw_key, value = item.split("=", 1)
        key = normalized_key(raw_key)
        if key in DEFAULTS:
            config[key] = coerce(key, value)

    config["api_key"] = "****"
    return config

app = FastAPI(title="12-Factor Config Precedence")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/effective-config")
def effective_config(set: Optional[List[str]] = Query(default=None)):
    return build_config(set)
