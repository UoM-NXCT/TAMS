import sys
import time

from PySide6.QtCore import QObject, QRunnable, Qt, QThreadPool, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class WorkerKilledException(Exception):
    """Exception raised when a worker is killed."""
    pass

class WorkerSignals(QObject):
    progress = Signal(int)

class JobRunner(QRunnable):

    signals = WorkerSignals()

    def __init__(self):
        super().__init__()
        self.is_paused = False
        self.is_killed = False

    @Slot()
    def run(self):
        """Perform the job."""
        for n in range(100):
            self.signals.progress.emit(n+1)
            time.sleep(0.1)

            while self.is_paused:
                time.sleep(0)
            if self.is_killed:
                raise WorkerKilledException

    def pause(self):
        """Pause the job."""

        self.is_paused = True

    def resume(self):
        """Resume the job."""

        self.is_paused = False

    def kill(self):
        """Kill the job."""

        self.is_killed = True

class ProgressDialogue(QDialog):
    def __init__(self):
        super().__init__()

        layout = QHBoxLayout()

        btn_stop = QPushButton("Stop")
        btn_pause = QPushButton("Pause")
        btn_resume = QPushButton("Resume")
        self.progress = QProgressBar()

        layout.addWidget(btn_stop)
        layout.addWidget(btn_pause)
        layout.addWidget(btn_resume)
        layout.addWidget(self.progress)

        self.setLayout(layout)



        # Thread runner
        self.threadpool = QThreadPool()

        # Create a runner
        self.runner = JobRunner()
        self.runner.signals.progress.connect(self.update_progress)
        self.threadpool.start(self.runner)

        btn_stop.pressed.connect(self.runner.kill)
        btn_pause.pressed.connect(self.runner.pause)
        btn_resume.pressed.connect(self.runner.resume)

        self.show()

    def update_progress(self, n):
        self.progress.setValue(n)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProgressDialogue()
    app.exec()