from src.engine import Engine
from src.cli.parser import CommandParser
from src.cli.command_handler import CommandHandler

def main():
    """The main entry point and REPL for the VTT application."""
    print("Welcome to the Modular VTT!")
    engine = Engine()
    parser = CommandParser()
    handler = CommandHandler(engine)

    # Auto-load our sample module to make testing easier.
    try:
        engine.load_system_module("dnd5e")
        print("Type 'help' for a list of commands, 'exit' to quit.")
    except FileNotFoundError:
        print("Error: Could not find the 'dnd5e' module.")
        print("Please make sure the 'modules/dnd5e' directory exists.")
        return

    while True:
        try:
            user_input = input('> ')
            if not user_input:
                continue

            command, args = parser.parse(user_input)

            if command:
                should_exit = handler.handle_command(command, args)
                if should_exit:
                    break

        except (EOFError, KeyboardInterrupt):
            # Allow exiting with Ctrl+D (EOFError) or Ctrl+C (KeyboardInterrupt)
            print("\nExiting.")
            break

if __name__ == "__main__":
    main()
