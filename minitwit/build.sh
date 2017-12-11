#!/bin/bash

#export MINITWIT_SETTINGS="/home/me/Dropbox-csuf/CSUF/476/project1/flask/examples/minitwit/minitwit/sessionDataOne.cfg"
#export FLASK_APP="minitwit"
#flask initdb && flask populatedb
#flask run
#./build1.sh > /dev/null 2>&1 &
export FLASK_APP="minitwit"
flask populatedb


mate-terminal -x bash -c 'sh ./build1.sh; exec bash' &
mate-terminal -x bash -c redis-server
# mate-terminal -x bash -c 'sh ./build2.sh; exec bash' &
# mate-terminal -x bash -c 'sh ./build3.sh; exec bash' &
mongo
