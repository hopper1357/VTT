import re
import random

class DiceRoller:
    """Parses and rolls dice expressions."""

    def roll(self, expression, entity=None, entity_manager=None):
        """
        Rolls dice based on a string expression like "1d20 + @strength_mod + 2".

        Args:
            expression (str): The dice expression to roll.
            entity (Entity, optional): The entity context for resolving variables.
            entity_manager (EntityManager, optional): The entity manager for resolving variables.

        Returns:
            dict: A dictionary containing the total, a list of dice rolls, and the total modifier.
        """
        # Tokenize the expression by splitting on + and - while keeping the delimiters
        tokens = re.split(r'([+-])', expression)

        total = 0
        all_rolls = []
        modifier_parts = []

        # Start with a default '+' operator for the first term
        operator = '+'

        for token in tokens:
            token = token.strip()
            if not token:
                continue

            if token in ['+', '-']:
                operator = token
                continue

            # This is a term (e.g., '1d20', '@strength_mod', '5')
            value = 0
            is_dice_roll = False

            # Dice roll term (e.g., "1d20", "2d6")
            dice_match = re.match(r"(\d+)d(\d+)", token)
            if dice_match:
                is_dice_roll = True
                num_dice = int(dice_match.group(1))
                num_sides = int(dice_match.group(2))
                rolls = [random.randint(1, num_sides) for _ in range(num_dice)]
                value = sum(rolls)
                all_rolls.extend(rolls)

            # Variable term (e.g., "@strength_mod")
            elif token.startswith('@'):
                if entity and entity_manager:
                    variable_name = token[1:]  # remove '@'
                    value = entity_manager.resolve_variable(variable_name, entity)
                else:
                    value = 0  # Cannot resolve variable without entity context

            # Constant term (e.g., "5")
            else:
                try:
                    value = int(token)
                except ValueError:
                    raise ValueError(f"Invalid term in dice expression: {token}")

            # Apply the operator to the value
            signed_value = value if operator == '+' else -value
            total += signed_value

            if not is_dice_roll:
                modifier_parts.append(signed_value)

        return {
            "total": total,
            "rolls": all_rolls,
            "modifier": sum(modifier_parts)
        }
