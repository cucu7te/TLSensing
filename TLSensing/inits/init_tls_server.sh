#!/bin/bash
cd $VIRTUAL_ENV/TLSensing
exec python manage.py runserver 0.0.0.0:8000 --insecure
