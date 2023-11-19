from typing import Callable, Any, Optional
from PyQt5 import QtCore, QtWidgets


class Thread(QtCore.QThread):
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.error = QtCore.pyqtBoundSignal()
        self.func: Callable[..., Any] = lambda: None
        self.result: Any = None

    def run(self) -> None:
        try:
            self.result = self.func()
        except Exception as e:
            self.error.emit(e)

    def start(
        self,
        priority: QtCore.QThread.Priority = QtCore.QThread.Priority.InheritPriority,
    ) -> None:
        super().start(priority=priority)

    def terminate(self) -> None:
        super().terminate()

    def get_result(self) -> Any:
        return self.result


def run_in_thread(
    func: Callable[..., Any],
    args: tuple[Any, ...] = (),
    on_finish: Optional[Callable[..., Any]] = None,
    on_error: Optional[Callable[..., Any]] = None,
) -> Thread:
    thread = Thread()
    thread.func = lambda: func(*args)
    if on_finish is not None:
        thread.finished.connect(on_finish)
    if on_error is not None:
        thread.error.connect(on_error)
    thread.start()
    return thread
