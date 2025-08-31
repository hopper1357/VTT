class View:
    """Base class for a view in the application."""

    def __init__(self, app):
        self.app = app

    def handle_event(self, event):
        """Handles a pygame event."""
        pass

    def update(self):
        """Updates the view's state."""
        pass

    def draw(self, screen):
        """Draws the view on the screen."""
        pass
