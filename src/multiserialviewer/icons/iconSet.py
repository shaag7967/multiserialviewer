from PySide6.QtGui import QIcon
import pathlib

class IconSet:
    def __init__(self, icon_set_name: str, color_name: str):
        icons_base_path = pathlib.Path(__file__).resolve().parent
        self.icons_dir_name = icons_base_path.joinpath(icon_set_name).joinpath(color_name)
        if not self.icons_dir_name.exists():
            raise Exception(f"Directory of IconSet '{self.icons_dir_name}' does not exist")

    # paths
    def getCaptureStartIconPath(self) -> str:
        return str(self.icons_dir_name.joinpath('capture_start.png'))

    def getCaptureStopIconPath(self) -> str:
        return str(self.icons_dir_name.joinpath('capture_stop.png'))

    def getErrorIconPath(self) -> str:
        return str(self.icons_dir_name.joinpath('error.png'))

    # icons
    def getHighlighterIcon(self) -> QIcon:
        return QIcon(str(self.icons_dir_name.joinpath('highlighter.png')))

    def getAppIcon(self) -> QIcon:
        return QIcon(str(self.icons_dir_name.joinpath('app.png')))

    def getSerialViewerIcon(self) -> QIcon:
        return QIcon(str(self.icons_dir_name.joinpath('serial_viewer.png')))

    def getCaptureStartIcon(self) -> QIcon:
        return QIcon(str(self.icons_dir_name.joinpath('capture_start.png')))

    def getCaptureStopIcon(self) -> QIcon:
        return QIcon(str(self.icons_dir_name.joinpath('capture_stop.png')))

    def getClearContentIcon(self) -> QIcon:
        return QIcon(str(self.icons_dir_name.joinpath('clear.png')))

    def getAddIcon(self) -> QIcon:
        return QIcon(str(self.icons_dir_name.joinpath('add.png')))

    def getSettingsIcon(self) -> QIcon:
        return QIcon(str(self.icons_dir_name.joinpath('settings.png')))

    def getDirectoryIcon(self) -> QIcon:
        return QIcon(str(self.icons_dir_name.joinpath('folder.png')))

    def getCascadeIcon(self) -> QIcon:
        return QIcon(str(self.icons_dir_name.joinpath('cascade.png')))

    def getTileIcon(self) -> QIcon:
        return QIcon(str(self.icons_dir_name.joinpath('tile.png')))

    def getCounterIcon(self) -> QIcon:
        return QIcon(str(self.icons_dir_name.joinpath('counter.png')))

    def getWatchIcon(self) -> QIcon:
        return QIcon(str(self.icons_dir_name.joinpath('watch.png')))

    def getSearchIcon(self) -> QIcon:
        return QIcon(str(self.icons_dir_name.joinpath('search.png')))

    def getStatsIcon(self) -> QIcon:
        return QIcon(str(self.icons_dir_name.joinpath('stats.png')))
