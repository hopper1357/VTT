#!/bin/bash

# A sequence of commands to simulate a game session
# Using a here-doc is a clean way to pipe multi-line input.
python3 main.py <<EOF
help
create char Player str=16 dex=14 hp=20
create char Goblin hp=7 dex=12
add Player
add Goblin
status
init
status
attack Goblin with Player
status
save test_game.sav
exit
EOF
