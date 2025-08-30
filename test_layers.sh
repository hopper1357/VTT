#!/bin/bash

# This script is for testing the map layering functionality.
# It places multiple objects on the same tile on different layers
# and verifies that only the top-most object is rendered.

python3 main.py <<EOF
create char Aragorn
map create forest 5 5
object place . forest 2 2 0
object place T forest 2 2 1
token place Aragorn forest 2 2
map view forest
exit
EOF
