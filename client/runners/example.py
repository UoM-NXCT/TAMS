import time

from .abstract import AbstractJobRunner


class ExampleRunner(AbstractJobRunner):
    def job(self):
        self.signals.progress.emit(1)
        time.sleep(0.1)
