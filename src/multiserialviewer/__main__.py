import sys
from multiserialviewer import __version__

from application.application import Application


def main() -> int | str:
    app = Application(__version__, sys.argv)
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
