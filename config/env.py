__all__ = ("BASE_DIR", "APPS_DIR", "env", "READ_DOT_ENV_FILE")

import pathlib

import environ

BASE_DIR = pathlib.Path(__file__).parent.parent
APPS_DIR = BASE_DIR / "apps"

env = environ.Env()

READ_DOT_ENV_FILE = env.bool("READ_DOT_ENV_FILE", default=True)

if READ_DOT_ENV_FILE:
    environ.Env.read_env(BASE_DIR / ".env")
