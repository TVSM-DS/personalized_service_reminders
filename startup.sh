#!/bin/bash
pip install -r requirements.txt --no-cache-dir
uvicorn app:app --host 0.0.0.0  --port 8000
