#!/bin/bash
status=$(supervisorctl status tls_push_server | grep RUNNING)
if [ "$status" == "" ]
then
 supervisorctl restart tls_push_server
fi

