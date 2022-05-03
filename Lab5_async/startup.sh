#!/bin/sh
curl -i -X PUT -d @config.json http://192.168.111.4:8500/v1/agent/service/register & 
python ./main.py