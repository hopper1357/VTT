import re
import random

class DiceRoller:
    """Parses and rolls dice expressions."""

    def __init__(self):
        # Pattern to capture NdN format, with an optional +/- modifier
        # e.g., "2d6", "1d20+5", "3d8 - 2"
        # Groups: 1: num_dice, 2: num_sides, 3: operator, 4: modifier
        # Added $ to the end to ensure the whole string matches
        self.pattern = re.compile(r"(\d+)d(\d+)(?:\s*([+-])\s*(\d+))?$")

    def roll(self, expression):
        """
        Rolls dice based on a string expression like "2d6+5".
        Returns a dictionary with the total, individual rolls, and modifier.
        """
        match = self.pattern.match(expression.strip())
        if not match:
            raise ValueError(f"Invalid dice expression: {expression}")

        num_dice = int(match.group(1))
        num_sides = int(match.group(2))
        operator = match.group(3)
        modifier = int(match.group(4)) if match.group(4) else 0

        if operator == '-':
            modifier = -modifier

        rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
        total = sum(rolls) + modifier

        return {
            "total": total,
            "rolls": rolls,
            "modifier": modifier
        }
