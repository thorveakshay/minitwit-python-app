#!/bin/bash
export FLASK_APP=minitwit
flask initdb && flask populatedb
flask run
