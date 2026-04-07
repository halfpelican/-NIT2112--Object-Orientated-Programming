"""Executable entry point that runs the club management demonstration."""

from pathlib import Path
import sys


# Allow importing the original monolithic script from the parent folder.
CURRENT_DIR = Path(__file__).resolve().parent
PARENT_DIR = CURRENT_DIR.parent
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

from club_management_starter import main


if __name__ == "__main__":
    main()
