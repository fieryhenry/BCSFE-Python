from typing import Optional
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget
import bcsfe


class TransferCodeInputBox(QtWidgets.QWidget):
    finished = QtCore.pyqtSignal()

    def __init__(self, parent: Optional[QWidget]) -> None:
        super().__init__(parent)
        self.result: Optional[bcsfe.core.ServerHandler] = None
        self.is_downloading = False
        self.init_ui()

    def init_ui(self) -> None:
        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self._layout)

        self.group_box = QtWidgets.QGroupBox("Transfer Code Input")
        self._layout.addWidget(self.group_box)
        self.group_box_layout = QtWidgets.QVBoxLayout()
        self.group_box.setLayout(self.group_box_layout)

        self.transfer_code_label = QtWidgets.QLabel("Transfer Code:")
        self.group_box_layout.addWidget(self.transfer_code_label)

        self.transfer_code_input = QtWidgets.QLineEdit()
        self.group_box_layout.addWidget(self.transfer_code_input)

        self.confirmation_code_label = QtWidgets.QLabel("Confirmation Code:")
        self.group_box_layout.addWidget(self.confirmation_code_label)

        self.confirmation_code_input = QtWidgets.QLineEdit()
        self.group_box_layout.addWidget(self.confirmation_code_input)

        self.country_code_dropdown = QtWidgets.QComboBox()
        for cc in bcsfe.core.CountryCode.get_all_str():
            self.country_code_dropdown.addItem(cc)

        self.group_box_layout.addWidget(self.country_code_dropdown)

        self.submit_button = QtWidgets.QPushButton("Download")
        self.group_box_layout.addWidget(self.submit_button)

        self.submit_button.clicked.connect(self.submit)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.group_box_layout.addWidget(self.cancel_button)

        self.cancel_button.clicked.connect(self.cancel)

        self.error_label = QtWidgets.QLabel()
        self.group_box_layout.addWidget(self.error_label)

        self.error_label.hide()

        self.group_box_layout.addStretch()

    def submit(self) -> None:
        transfer_code = self.transfer_code_input.text()
        confirmation_code = self.confirmation_code_input.text()
        country_code = bcsfe.core.CountryCode.from_code(
            self.country_code_dropdown.currentText()
        )
        if transfer_code == "" or confirmation_code == "":
            return

        if self.is_downloading:
            return
        self.error_label.hide()
        self.is_downloading = True
        self.submit_button.setEnabled(False)
        self.submit_button.setText("Downloading...")

        gv = bcsfe.core.GameVersion.from_string("12.2.0")

        self.download_thread = bcsfe.ui.thread.run_in_thread(
            bcsfe.core.ServerHandler.from_codes,
            args=(transfer_code, confirmation_code, country_code, gv, False),
            on_finish=self.on_finish,
        )

    def on_finish(self) -> None:
        self.is_downloading = False
        result = self.download_thread.get_result()
        self.submit_button.setEnabled(True)
        self.submit_button.setText("Download")
        if result is None:
            self.error_label.setText("Invalid transfer code")
            self.error_label.show()
            return
        self.result = result

        self.finished.emit()

    def cancel(self) -> None:
        if self.is_downloading:
            self.download_thread.terminate()
        self.close()
