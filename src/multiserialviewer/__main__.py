import sys
from multiserialviewer import __version__


def main() -> int | str:
    print(__version__)
    return 0


if __name__ == '__main__':
    sys.exit(main())
