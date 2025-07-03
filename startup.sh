#!/bin/bash
pip install -r requirements.txt
#python app.py
gunicorn --bind 0.0.0.0:${WEBSITES_PORT:-8000} app:app