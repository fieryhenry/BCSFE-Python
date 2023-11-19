from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import bcsfe


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("BCSFE")
        self.resize(800, 600)
        self.create_menu()

    def create_menu(self):
        self.menu = QtWidgets.QMenuBar()
        self.setMenuBar(self.menu)
        self.file_menu = QtWidgets.QMenu("File")
        self.menu.addMenu(self.file_menu)
        self.edit_menu = QtWidgets.QMenu("Edit")
        self.menu.addMenu(self.edit_menu)
        self.view_menu = QtWidgets.QMenu("View")
        self.menu.addMenu(self.view_menu)
        self.help_menu = QtWidgets.QMenu("Help")
        self.menu.addMenu(self.help_menu)

        self.main_widget = QtWidgets.QGroupBox(self)
        self._layout = QtWidgets.QVBoxLayout(
            self.main_widget,
        )
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(self.main_widget)

        self.create_file_menu()
        # self.create_edit_menu()
        # self.create_view_menu()
        # self.create_help_menu()

        self.disable_save_options()

    def load_from_save_file(self):
        path = bcsfe.cli.file_dialog.FileDialog().get_file(
            "Select save file",
            [
                ("All Files", "*"),
                ("Exported JSON Save File", ".json"),
            ],
            initialdir=bcsfe.core.SaveFile.get_saves_path().to_str(),
            initialfile="SAVE_DATA",
        )
        if path is None:
            return
        path = bcsfe.core.Path(path)
        self.load_from_file(path)

    def disable_save_options(self):
        self.save_action.setEnabled(False)
        self.save_as_action.setEnabled(False)
        self.save_to_transfer_codes_action.setEnabled(False)
        self.save_to_adb_action.setEnabled(False)

    def enable_save_options(self):
        self.save_action.setEnabled(True)
        self.save_as_action.setEnabled(True)
        self.save_to_transfer_codes_action.setEnabled(True)
        self.save_to_adb_action.setEnabled(True)

    def load_from_file(self, path: bcsfe.core.Path):
        if path.get_extension() == "json":
            json = bcsfe.core.JsonFile.from_path(path)
            self.save = bcsfe.core.SaveFile.from_dict(json.to_object())
            path = path.remove_extension()
            self.save.to_file(path)
            self.save.save_path = path
        else:
            self.save = bcsfe.core.SaveFile(path.read())
            self.save.save_path = path

        self.save.save_path.copy_thread(self.save.get_default_path())

        self.enable_save_options()

    def load_from_transfer_codes(self):
        if self.transfer_code_input_box is not None:
            self._layout.removeWidget(self.transfer_code_input_box)
        self.transfer_code_input_box = bcsfe.ui.server_handler.TransferCodeInputBox(
            self.main_widget
        )
        self._layout.addWidget(self.transfer_code_input_box)
        self.transfer_code_input_box.finished.connect(self.finished_load_transfer_codes)

    def finished_load_transfer_codes(self):
        if self.transfer_code_input_box is None:
            return
        result = self.transfer_code_input_box.result
        if result is None:
            return
        self.save = result.save_file
        self._layout.removeWidget(self.transfer_code_input_box)

    def create_file_menu(self):
        self.load_from_file_action = QtWidgets.QAction("Load save from file", self)
        self.load_from_file_action.setShortcut("Ctrl+O")
        self.load_from_file_action.setStatusTip("Load save data from file")
        self.load_from_file_action.triggered.connect(self.load_from_save_file)
        self.file_menu.addAction(self.load_from_file_action)  # type: ignore

        self.load_from_transfer_codes_action = QtWidgets.QAction(
            "Load from transfer codes", self
        )
        self.load_from_transfer_codes_action.setShortcut("Ctrl+Shift+O")
        self.load_from_transfer_codes_action.setStatusTip(
            "Load save data from transfer codes"
        )
        self.load_from_transfer_codes_action.triggered.connect(
            self.load_from_transfer_codes
        )
        self.file_menu.addAction(self.load_from_transfer_codes_action)  # type: ignore
        self.transfer_code_input_box = None

        self.load_from_adb_action = QtWidgets.QAction("Load save from adb", self)
        self.load_from_adb_action.setShortcut("Ctrl+Shift+Alt+O")
        self.load_from_adb_action.setStatusTip("Load save data from adb")
        self.file_menu.addAction(self.load_from_adb_action)  # type: ignore

        self.separator = QtWidgets.QAction(self)
        self.separator.setSeparator(True)
        self.file_menu.addAction(self.separator)  # type: ignore

        self.save_action = QtWidgets.QAction("Save save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.setStatusTip("Save save data to file")
        self.file_menu.addAction(self.save_action)  # type: ignore

        self.save_as_action = QtWidgets.QAction("Save save as", self)
        self.save_as_action.setShortcut("Ctrl+Shift+S")
        self.save_as_action.setStatusTip("Save save data to a specific file or format")
        self.file_menu.addAction(self.save_as_action)  # type: ignore

        self.save_to_transfer_codes_action = QtWidgets.QAction(
            "Save to transfer codes", self
        )
        self.save_to_transfer_codes_action.setShortcut("Ctrl+Alt+S")
        self.save_to_transfer_codes_action.setStatusTip(
            "Save save data to transfer codes"
        )
        self.file_menu.addAction(self.save_to_transfer_codes_action)  # type: ignore

        self.save_to_adb_action = QtWidgets.QAction("Save to adb", self)
        self.save_to_adb_action.setShortcut("Ctrl+Shift+Alt+S")
        self.save_to_adb_action.setStatusTip("Save save data to adb")
        self.file_menu.addAction(self.save_to_adb_action)  # type: ignore

        self.separator = QtWidgets.QAction(self)
        self.separator.setSeparator(True)
        self.file_menu.addAction(self.separator)  # type: ignore

        self.exit_action = QtWidgets.QAction("Exit", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.setStatusTip("Exit application")
        self.exit_action.triggered.connect(self.exit)
        self.file_menu.addAction(self.exit_action)  # type: ignore

    def exit(self):
        self.close()


def run():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
