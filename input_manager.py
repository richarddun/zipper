from collections import defaultdict
from kivy.core.window import Window


class InputManager:
    """Simple keyboard input handler maintaining key states."""

    def __init__(self):
        self.keys = defaultdict(lambda: False)
        Window.bind(on_key_down=self.on_key_down, on_key_up=self.on_key_up)

    def on_key_down(self, window, keycode, *args):
        self.keys[keycode] = True

    def on_key_up(self, window, keycode, *args):
        self.keys[keycode] = False

    def is_pressed(self, keycode):
        """Return True if the given keycode is currently pressed."""
        return self.keys.get(keycode, False)


# Global instance used throughout the project
input_manager = InputManager()
