#!/bin/bash

echo "Running Filebeat"
# filebeat setup --modules=apache --pipelines
# service filebeat start
# service filebeat status

echo "starting Servvice"
flask run --host 0.0.0.0 --port 5000
# gunicorn django_web.wsgi:application --log-level=debug --bind 0.0.0.0:8000 --workers 2
