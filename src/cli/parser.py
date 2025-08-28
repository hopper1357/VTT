import shlex

class CommandParser:
    """Parses user input strings into commands and arguments."""

    def parse(self, input_string):
        """
        Parses a string into a command and a list of arguments.

        Args:
            input_string (str): The raw string from the user.

        Returns:
            tuple: A tuple containing the command (str) and arguments (list),
                   or (None, []) if the input is empty.
        """
        if not input_string:
            return None, []

        try:
            parts = shlex.split(input_string)
            command = parts[0].lower()
            args = parts[1:]
            return command, args
        except ValueError:
            # shlex can raise ValueError on unclosed quotes
            print("Error: Unmatched quotes in command.")
            return None, []
