#!/bin/bash

# This script is for testing the map background asset functionality.

python3 main.py <<EOF
map create road_map 10 5 bg=StraightRoadPublicJPG.jpg
map view road_map
save test_background.json
load test_background.json
map view road_map
exit
EOF
