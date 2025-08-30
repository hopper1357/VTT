#!/bin/bash
# This script verifies that lighting properties can be added to objects
# and are correctly persisted.

python3 main.py <<EOF
create char Player
map create dungeon 10 10
# Place a pillar that blocks light
object place '#' dungeon 5 5 1 blocks=true
# Place the player with a light source
token place Player dungeon 3 5 4 light=5
# View the map and check the object list for properties
map view dungeon
save test_fov.json
load test_fov.json
# View again to check persistence
map view dungeon
exit
EOF
