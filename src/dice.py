import re
import random

class DiceRoller:
    """Parses and rolls dice expressions."""

    def roll(self, expression, entity=None, entity_manager=None):
        """
        Rolls dice based on a string expression like "1d20 + @strength_mod + 2".
        Supports advantage (_adv) and disadvantage (_dis) on dice terms.

        Args:
            expression (str): The dice expression to roll.
            entity (Entity, optional): The entity context for resolving variables.
            entity_manager (EntityManager, optional): The entity manager for resolving variables.

        Returns:
            dict: A dictionary containing the total, a list of chosen dice rolls,
                  the total modifier, and a list of details about the roll.
        """
        # Tokenize the expression by splitting on + and - while keeping the delimiters
        tokens = re.split(r'([+-])', expression)

        total = 0
        all_rolls = []
        modifier_parts = []
        roll_details = []

        # Start with a default '+' operator for the first term
        operator = '+'

        for token in tokens:
            token = token.strip()
            if not token:
                continue

            if token in ['+', '-']:
                operator = token
                continue

            # This is a term (e.g., '1d20', '@strength_mod', '5', '1d20_adv')
            value = 0
            is_dice_roll = False

            # Dice roll term (e.g., "1d20", "2d6", "1d20_adv")
            dice_match = re.match(r"(\d+)d(\d+)(_adv|_dis)?", token)
            if dice_match:
                is_dice_roll = True
                num_dice = int(dice_match.group(1))
                num_sides = int(dice_match.group(2))
                suffix = dice_match.group(3)

                # Helper to perform a single roll of the dice
                roll_once = lambda: [random.randint(1, num_sides) for _ in range(num_dice)]

                rolls = []
                if suffix == '_adv':
                    rolls1 = roll_once()
                    rolls2 = roll_once()
                    if sum(rolls1) >= sum(rolls2):
                        rolls = rolls1
                    else:
                        rolls = rolls2
                    roll_details.append(f"Advantage on {num_dice}d{num_sides}: Rolled {rolls1} and {rolls2}, chose {rolls}.")
                elif suffix == '_dis':
                    rolls1 = roll_once()
                    rolls2 = roll_once()
                    if sum(rolls1) <= sum(rolls2):
                        rolls = rolls1
                    else:
                        rolls = rolls2
                    roll_details.append(f"Disadvantage on {num_dice}d{num_sides}: Rolled {rolls1} and {rolls2}, chose {rolls}.")
                else:  # No suffix, a normal roll
                    rolls = roll_once()

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
            "modifier": sum(modifier_parts),
            "details": roll_details
        }
