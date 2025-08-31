import asyncio
import sys
import uvicorn

from src.engine import Engine
from src.network import Server, Client
from src.server import create_app
from src.gui.app import App
import pygame


async def handle_user_input(client):
    """Handles user input in a non-blocking way and sends it to the server."""
    loop = asyncio.get_event_loop()
    while True:
        try:
            user_input = await loop.run_in_executor(None, lambda: input('> '))
            if not user_input:
                continue
            if user_input.strip().lower() == 'exit':
                break
            await client.send_message(user_input)
        except (EOFError, KeyboardInterrupt):
            break
    print("\nExiting.")


async def main_async():
    """The async main entry point for the client."""
    if len(sys.argv) != 4:
        print("Usage: connect <ip> <port>")
        return

    ip, port = sys.argv[2], int(sys.argv[3])

    engine = Engine()
    client = Client(ip, port, engine)
    if not await client.connect():
        return

    listener_task = asyncio.create_task(client.listen())
    await handle_user_input(client)

    listener_task.cancel()
    await client.disconnect()


def main():
    """The main entry point for the VTT application."""
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <mode> [options]")
        print("Modes:")
        print("  host <port>          - Start a new session as the Game Master.")
        print("  connect <ip> <port> - Connect to a session as a Player.")
        print("  gui                  - Run the graphical user interface.")
        print("  local                - Run in single-player offline mode.")
        return

    mode = sys.argv[1].lower()

    if mode == "host":
        if len(sys.argv) != 3:
            print("Usage: host <port>")
            return
        port = int(sys.argv[2])

        engine = Engine()
        try:
            engine.load_system_module("dnd5e")
        except FileNotFoundError:
            print("Error: Could not find the 'dnd5e' module.")
            return

        app = create_app(engine)

        print(f"Starting server on port {port}...")
        print("The GM should connect using a separate client.")
        uvicorn.run(app, host="0.0.0.0", port=port)

    elif mode == "connect":
        try:
            asyncio.run(main_async())
        except KeyboardInterrupt:
            print("\nClient terminated.")

    elif mode == "gui":
        print("Starting the GUI...")
        pygame.init()            # Initialize Pygame (including fonts)
        engine = Engine()
        gui_app = App(engine)
        gui_app.run()

    elif mode == "local":
        print("Starting local single-player session...")
        engine = Engine()
        engine.load_system_module("dnd5e")
        # You can add a local CLI loop here if needed
        print("Local session started. Type 'exit' to quit.")
        while True:
            try:
                cmd = input("> ")
                if cmd.strip().lower() == "exit":
                    break
                engine.execute_command(cmd)
            except (KeyboardInterrupt, EOFError):
                break
        print("Local session ended.")

    else:
        print(f"Unknown mode: '{mode}'")


if __name__ == "__main__":
    main()
