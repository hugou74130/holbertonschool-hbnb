# redirect create_app to the app package implementation
from app import create_app

# this module exists to allow `from app import create_app` when
# the top-level directory is on sys.path (e.g. when running tests or
# `python -m run`).
