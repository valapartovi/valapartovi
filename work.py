from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import QThread, pyqtSignal
import time

class TimerWorker(QThread):
    update_time = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._running = True
        self.seconds = 0

    def run(self):
        while self._running:
            time.sleep(1)
            self.seconds += 1
            minutes = self.seconds // 60
            secs = self.seconds % 60
            self.update_time.emit(f"{minutes:02}:{secs:02}")

    def stop(self):
        self._running = False

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تایمر با QThread")
        self.setGeometry(200, 200, 250, 100)

        self.label = QLabel("00:00", self)
        self.label.setStyleSheet("font-size: 24pt; text-align: center;")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.timer_thread = TimerWorker()
        self.timer_thread.update_time.connect(self.update_label)
        self.timer_thread.start()

    def update_label(self, text):
        self.label.setText(text)

    def closeEvent(self, event):
        self.timer_thread.stop()
        self.timer_thread.quit()
        self.timer_thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication([])
    win = MyApp()
    win.show()
    app.exec_()
