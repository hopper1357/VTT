#!/bin/bash

python3 main.py <<EOF
load test_game.sav
status
exit
EOF

# Clean up the save file
rm test_game.sav
