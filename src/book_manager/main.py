from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from book_manager.ui.console import ConsoleUI, Servicios


def main():
    ConsoleUI(Servicios()).run()


if __name__ == "__main__":
    main()
