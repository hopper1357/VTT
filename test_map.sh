#!/bin/bash

# This script is for testing the map and token functionality.

python3 main.py <<EOF
create char Aragorn hp=100
create char Sauron hp=500
map create middle-earth 10 5
map list
token place Aragorn middle-earth 2 3
map view middle-earth
save test_game.json
load test_game.json
map view middle-earth
exit
EOF
