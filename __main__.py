from .main import ZippyApp
# Import the input manager so that it binds to the Window on module load
from .input_manager import input_manager  # noqa: F401


def main():
    ZippyApp().run()


if __name__ == "__main__":
    main()

