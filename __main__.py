from kivy.core.window import Window
from .main import ZippyApp, keys


def on_key_down(window, keycode, *rest):
    keys[keycode] = True


def on_key_up(window, keycode, *rest):
    keys[keycode] = False


def main():
    Window.bind(on_key_down=on_key_down, on_key_up=on_key_up)
    ZippyApp().run()


if __name__ == "__main__":
    main()
