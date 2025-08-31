from enum import Enum
import uuid

class UserRole(Enum):
    """Defines the roles a user can have."""
    GM = "GM"
    PLAYER = "PLAYER"

class User:
    """Represents a user in the game."""
    def __init__(self, username, role=UserRole.PLAYER):
        self.id = str(uuid.uuid4())
        self.username = username
        self.role = role

    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}', role={self.role.name})"

class UserManager:
    """Manages all users in the game session."""
    def __init__(self):
        self._users = {} # Maps user_id to User object
        self._gm = None

    def add_user(self, user):
        """Adds a user to the manager."""
        if user.role == UserRole.GM:
            if self._gm:
                raise ValueError("A Game Master already exists for this session.")
            self._gm = user

        if user.id in self._users:
            raise ValueError(f"User with ID {user.id} already exists.")

        self._users[user.id] = user
        print(f"User '{user.username}' ({user.role.name}) connected.")
        return user

    def remove_user(self, user_id):
        """Removes a user from the manager."""
        user = self._users.pop(user_id, None)
        if user:
            if user.role == UserRole.GM:
                self._gm = None
            print(f"User '{user.username}' disconnected.")
        return user

    def get_user(self, user_id):
        """Retrieves a user by their ID."""
        return self._users.get(user_id)

    def find_user_by_name(self, username):
        """Finds a user by their username."""
        for user in self._users.values():
            if user.username.lower() == username.lower():
                return user
        return None

    def get_gm(self):
        """Returns the Game Master user."""
        return self._gm

    def list_users(self):
        """Returns a list of all users."""
        return list(self._users.values())
