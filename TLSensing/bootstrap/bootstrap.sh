#!/bin/bash
# Author: Gianfranco Micoli <micoli.gianfranco@gmail.com>
# This script installs TLSensing inside a virtualenv
# Usage: bootstrap.sh virtualenv_path

if [ -z "$1" ]; then
	echo Usage: bootstrap.sh virtualenv_path
	exit 1
fi

if [ ! -f $1/bin/activate ]; then
	echo $1/bin/activate not found. Please specify a valid virtualenv path
else
	echo Bootstrapping to $1...
	source $1/bin/activate
	pip install -U pip setuptools --egg scons
	pip --no-cache-dir install -r $1/TLSensing/requirements.txt
	cp -r data/* $1/
	mv $1/bin/supervisord $1/bin/tls-supervisord-bin
	mv $1/bin/supervisorctl $1/bin/tls-supervisorctl-bin
	mkdir -p $1/var/log/supervisor
	for service in `ls -1 data/etc/supervisor/conf.d/ | cut -d "." -f 1`; do
		mkdir -p $1/var/log/$service
	done
	mkdir -p $1/var/run
	sed -i -e "s#/path/to/TLSEnv#$1#g" $1/bin/start_tlsensing
	echo DONE! You can now run TLSensing by starting $1/bin/start_tlsensing
fi
