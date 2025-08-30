#!/bin/bash

# This script is for testing the hex grid functionality.

python3 main.py <<EOF
create char Gandalf
map create hextest 8 4 type=hex
token place Gandalf hextest 2 1
map view hextest
save test_hex.json
load test_hex.json
map view hextest
exit
EOF
