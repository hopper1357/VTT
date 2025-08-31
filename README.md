# Modular Virtual Tabletop (VTT)

This is a command-line based, modular virtual tabletop application designed to be system-agnostic.

## Multiplayer Guide

This VTT now supports a client-server multiplayer model. One player acts as the **Game Master (GM)**, who hosts the session and has full control. Other players can connect as **Players**, who have limited permissions.

### Starting a Session (GM)

To host a game, you must start the application in `host` mode. Choose a port for other players to connect to.

```bash
python main.py host <port>
```

Example:
```bash
python main.py host 8888
```
This will start the server and give you a command prompt. You are now the GM.

### Joining a Session (Player)

To join an existing game, you need the IP address and port of the GM's session. Start the application in `connect` mode.

```bash
python main.py connect <ip_address> <port>
```

Example:
```bash
python main.py connect 127.0.0.1 8888
```
This will connect you to the session. You will receive the current game state automatically.

### Multiplayer Commands

There are several new commands to manage the multiplayer session:

*   **`players`**: Lists all users currently connected to the session, along with their role (GM or Player).
    ```
    > players
    --- Connected Players ---
      - GameMaster (GM)
      - Player-54321 (PLAYER)
    -------------------------
    ```

*   **`assign <token_name> to <player_name>`**: (GM Only) This command gives a player control over a specific token.
    -   `<token_name>`: The name of the character/entity associated with the token.
    -   `<player_name>`: The name of the player you want to assign the token to (you can see this from the `players` command).

    Example:
    ```
    > assign Goblin to Player-54321
    ```
    After this, "Player-54321" will be able to move the "Goblin" token. Players can also move any token whose owner is set to `ALL_PLAYERS`.
