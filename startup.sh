#!/bin/bash

pip install -r requirements.txt --no-cache-dir
gunicorn --bind 0.0.0.0:${WEBSITES_PORT:-8000} app:app

