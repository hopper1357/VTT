#!/bin/bash

# This script is for testing the object remove functionality.
# It verifies that the command is recognized and that error handling
# for a non-existent object ID works as expected.

python3 main.py <<EOF
map create testmap 5 5
object remove fake-id testmap
exit
EOF
