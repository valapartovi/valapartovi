import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QHBoxLayout, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QIntValidator

class ControlledWindow(QWidget):
    def __init__(self, index, controller):
        super().__init__()
        self.index = index
        self.controller = controller
        self.setWindowTitle(f"پنجره {index + 1}")
        layout = QHBoxLayout()
        for task_name in ['x', 'y', 'z']:
            label = QLabel(task_name)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label)
        self.setLayout(layout)

    def closeEvent(self, event):
        # وقتی پنجره بسته شد، به کنترلر اطلاع می‌دهیم تا حذفش کنه و چیدمان رو به‌روز کنه
        self.controller.window_closed(self)
        event.accept()

class ControllerWindow(QWidget):
    def __init__(self, windows, main_window):
        super().__init__()
        self.setWindowTitle("کنترل پنجره‌ها")
        self.windows = windows  # لیست پنجره‌ها (بدون None)
        self.main_window = main_window
        self.setup_ui()

    def setup_ui(self):
        self.resize(400, 50)
        layout = QHBoxLayout()

        self.btn_close_all = QPushButton("بستن همه پنجره‌ها")
        self.btn_close_all.clicked.connect(self.close_all)
        layout.addWidget(self.btn_close_all)

        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout.addItem(spacer)

        self.btn_add_window = QPushButton("اضافه کردن پنجره")
        self.btn_add_window.clicked.connect(self.add_window)
        layout.addWidget(self.btn_add_window)

        self.setLayout(layout)

        screen = QApplication.primaryScreen()
        geom = screen.availableGeometry()
        x = geom.x()
        y = geom.y() + geom.height() - self.height() - 50
        self.move(x + 50, y)

    def close_all(self):
        for w in self.windows:
            w.close()
        self.windows.clear()
        self.close()
        self.main_window.close()

    def add_window(self):
        if len(self.windows) >= 16:
            QMessageBox.warning(self, "هشدار", "به نهایت تعداد پنجره (16) رسیدید.")
            return

        new_index = len(self.windows)
        new_window = ControlledWindow(new_index, self)
        self.windows.append(new_window)
        self.rearrange_windows()

    def rearrange_windows(self):
        n = len(self.windows)
        if n == 0:
            return

        screen = QApplication.primaryScreen()
        screen_geom = screen.availableGeometry()
        screen_width = screen_geom.width()
        screen_height = screen_geom.height()

        max_usage_ratio = 0.8

        cols = math.ceil(math.sqrt(n))
        rows = math.ceil(n / cols)

        max_width_per_window = int((screen_width * max_usage_ratio) // cols)
        max_height_per_window = int((screen_height * max_usage_ratio) // rows)

        total_width = max_width_per_window * cols
        total_height = max_height_per_window * rows

        offset_x = int((screen_width - total_width) // 2 + screen_geom.x())
        offset_y = int((screen_height - total_height) // 2 + screen_geom.y())

        if max_width_per_window < 100 or max_height_per_window < 100:
            QMessageBox.warning(self, "خطا", "پنجره‌ها خیلی کوچک شده‌اند. عدد کمتری وارد کنید یا بعضی پنجره‌ها را ببندید.")
            return

        for i, w in enumerate(self.windows):
            w.setWindowTitle(f"پنجره {i + 1}")
            row = i // cols
            col = i % cols
            w.setGeometry(QRect(
                offset_x + col * max_width_per_window,
                offset_y + row * max_height_per_window,
                max_width_per_window,
                max_height_per_window
            ))
            w.show()

    def window_closed(self, window):
        # حذف پنجره از لیست و چیدمان مجدد
        if window in self.windows:
            self.windows.remove(window)
            self.rearrange_windows()
            if len(self.windows) == 0:
                # اگر همه پنجره‌ها بسته شدند، کنترلر و پنجره اصلی را هم ببندیم
                self.close()
                self.main_window.close()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.label = QLabel("تعداد پنجره‌ها را وارد کنید (1 تا 16):")
        self.layout.addWidget(self.label)

        self.input = QLineEdit()
        self.input.setValidator(QIntValidator(1, 1000))
        self.layout.addWidget(self.input)

        self.btn = QPushButton("باز کردن پنجره‌ها")
        self.btn.clicked.connect(self.open_windows)
        self.layout.addWidget(self.btn)

        self.setLayout(self.layout)

        self.windows = []
        self.controller = None

    def open_windows(self):
        text = self.input.text()
        if not text:
            return
        n = int(text)
        if n > 16:
            QMessageBox.warning(self, "خطا", "تعداد پنجره‌ها نمی‌تواند بیشتر از 16 باشد.")
            return
        if n <= 0:
            return

        # بستن پنجره‌های قبلی
        if self.controller is not None:
            self.controller.close_all()

        self.windows = []
        for i in range(n):
            w = ControlledWindow(i, None)
            self.windows.append(w)

        self.controller = ControllerWindow(self.windows, self)

        # ست کردن کنترلر برای هر پنجره
        for w in self.windows:
            w.controller = self.controller

        self.controller.rearrange_windows()

        self.hide()
        self.controller.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
