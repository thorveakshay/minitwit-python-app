#!/bin/bash
export MINITWIT_SETTINGS="/home/me/Dropbox-csuf/CSUF/476/project1/flask/examples/minitwit/minitwit/sessionDataOne.cfg"
export FLASK_APP="minitwit"
flask initdb && flask populatedb
flask run -h 127.0.0.1 -p 5000
