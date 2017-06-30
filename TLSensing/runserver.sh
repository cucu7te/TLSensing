#!/usr/bin/env bash

PYTHONPATH="$PYTHONPATH:coap" ./manage.py runserver 0.0.0.0:8000 --insecure
