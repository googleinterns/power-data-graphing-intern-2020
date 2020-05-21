#!/bin/bash
source ../venv/bin/activate
pip3 install -r requirements.txt
export FLASK_APP=main.py
export FLASK_ENV=development
flask run
deactivate