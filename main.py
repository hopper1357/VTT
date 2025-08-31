import asyncio
import sys
from src.engine import Engine
from src.network import Server, Client
from src.gui.app import App

async def handle_user_input(engine, client_or_server=None):
    """Handles user input in a non-blocking way."""
    loop = asyncio.get_event_loop()
    handler = engine.get_command_handler()

    while True:
        try:
            # Use run_in_executor to avoid blocking the event loop with input()
            user_input = await loop.run_in_executor(None, lambda: input('> '))
            if not user_input:
                continue

            if user_input.strip().lower() == 'exit':
                break

            # If we are a client, send the command to the server
            if isinstance(client_or_server, Client):
                # The client sends the raw command string
                await client_or_server.send_message(user_input)
            else:  # We are the server (or offline)
                # The server executes the command directly
                handler.parse_and_handle(user_input)
                # If we are the server, broadcast the executed command
                if isinstance(client_or_server, Server):
                    await client_or_server.broadcast(user_input)

        except (EOFError, KeyboardInterrupt):
            break

    print("\nExiting.")


async def main():
    """The main entry point and REPL for the VTT application."""
    print("Welcome to the Modular VTT!")

    if len(sys.argv) < 2:
        print("Usage: python main.py <mode> [options]")
        print("Modes:")
        print("  host <port>   - Start a new session as the Game Master.")
        print("  connect <ip> <port> - Connect to a session as a Player.")
        print("  local         - Run in single-player offline mode.")
        print("  gui           - Run the graphical user interface.")
        return

    mode = sys.argv[1].lower()
    engine = Engine()

    # Auto-load our sample module to make testing easier.
    try:
        engine.load_system_module("dnd5e")
    except FileNotFoundError:
        print("Error: Could not find the 'dnd5e' module.")
        print("Please make sure the 'modules/dnd5e' directory exists.")
        return

    if mode == "host":
        if len(sys.argv) != 3:
            print("Usage: host <port>")
            return
        port = int(sys.argv[2])
        server = Server('0.0.0.0', port, engine)
        await server.start()
        await handle_user_input(engine, server)
        await server.stop()

    elif mode == "connect":
        if len(sys.argv) != 4:
            print("Usage: connect <ip> <port>")
            return
        ip, port = sys.argv[2], int(sys.argv[3])
        client = Client(ip, port, engine)
        if not await client.connect():
            return

        # Start listening for server messages in the background
        listener_task = asyncio.create_task(client.listen())

        await handle_user_input(engine, client)

        # Clean up
        listener_task.cancel()
        await client.disconnect()

    elif mode == "local":
        print("Running in local mode. Type 'help' for commands, 'exit' to quit.")
        await handle_user_input(engine)

    elif mode == "gui":
        print("Starting the GUI...")
        gui_app = App(engine)
        gui_app.run()

    else:
        print(f"Unknown mode: '{mode}'")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nApplication terminated.")
