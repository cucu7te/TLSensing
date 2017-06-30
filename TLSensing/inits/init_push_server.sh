#!/bin/bash
cd $VIRTUAL_ENV/TLSensing
exec python manage.py pushServer 5684 sens
