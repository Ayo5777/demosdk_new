#!/bin/bash

cd "$(dirname "$0")"
source env/bin/activate
uvicorn src.main:app --host=127.0.0.1:8000 --workers=2