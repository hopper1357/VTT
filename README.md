# Modular Virtual Tabletop (VTT)

## Overview

This project is a backend engine for a modular Virtual Tabletop (VTT) designed to be system-agnostic. It provides a core set of features for running tabletop role-playing games, including entity management, a dice roller, and a map/token system. The engine is driven by a command-line interface (CLI).

## How to Run

The application is run through the `main.py` script. It accepts a series of commands from standard input.

You can run a script of commands like this:
```bash
python3 main.py < my_command_script.txt
```

Or you can run it interactively by typing commands directly into the console:
```bash
python3 main.py
> create char Player hp=20
> ...
```

## Command Reference

The following commands are available in the CLI:

### General Commands
- `help`: Shows the help message with a list of all commands.
- `status`: Shows the current game status, including the initiative order and combatant health.
- `save <filepath>`: Saves the current game state to a file.
- `load <filepath>`: Loads a game state from a file.
- `exit`: Exits the application.

### Character & Combat Commands
- `create char <name> [hp=X] [dex=Y]...`: Creates a new character entity with the given name and attributes.
- `add <name>`: Adds a character to the initiative tracker for combat.
- `init`: Rolls initiative for all combatants in the tracker.
- `attack <target> with <actor>`: Executes a default attack from an actor against a target.

### Map & Object Commands
- `map create <name> <width> <height> [type=hex] [bg=path]`: Creates a new map with a given name, dimensions, and optional grid type or background image path.
- `map list`: Lists all created maps.
- `map view <map_name>`: Displays a text-based representation of a map and the objects on it.
- `token place <entity> <map> <x> <y> [layer=N]`: Places a token for an entity onto a map at the specified coordinates and layer.
- `object place <char> <map> <x> <y> <layer>`: Places a generic map object represented by a single character on the map.
- `object move <id> <map> <x> <y>`: Moves an existing object or token to new coordinates.
- `object remove <id> <map>`: Removes an object or token from a map using its unique ID.

### Drawing & Grouping Commands
- `shape place <type> <map> <x> <y> [opts]`: Places a shape on a map. Optional arguments (`[opts]`) can be `layer=N`, `size=N`, `stroke_color=#hex`, `fill_color=#hex`, `opacity=0.N`, etc.
- `draw path <map> <x,y>... [opts]`: Draws a path with a series of points (e.g., `10,20 15,25`). Optional arguments are the same as for shapes.
- `group create <map> <id1> <id2>...`: Groups multiple objects together. The new group can then be moved by its own ID.

## Example Usage

Here is an example of a script that can be piped into the application to simulate a short game session:

```
# commands.txt
create char Player str=16 dex=14 hp=20
create char Goblin hp=7 dex=12

add Player
add Goblin

status
init
status

attack Goblin with Player
status

save test_game.json
```

Run the script with:
```bash
python3 main.py < commands.txt
```
