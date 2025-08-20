import sys
import random
import threading
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit, QPushButton, QLabel, QVBoxLayout
)
from PyQt5.QtGui import QPixmap, QIcon, QCursor
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QPoint, QTimer, QEvent, pyqtSignal


class FloatingMessage(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            "background-color: rgba(255, 255, 0, 220);"
            "color: black; font-size: 16pt; border: 2px solid black; border-radius: 10px;"
            "padding: 10px;"
        )
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(300, 50)
        self.hide()

    def show_message(self, text):
        self.setText(text)
        start_x = (self.parent().width() - self.width()) // 2
        start_y = 0
        end_y = (self.parent().height() - self.height()) // 2

        self.move(start_x, start_y)
        self.show()

        self.anim = QPropertyAnimation(self, b"pos", self)
        self.anim.setDuration(700)
        self.anim.setStartValue(QPoint(start_x, start_y))
        self.anim.setEndValue(QPoint(start_x, end_y))
        self.anim.start()

        QTimer.singleShot(2000, self.hide_message)

    def hide_message(self):
        start_pos = self.pos()
        end_pos = QPoint(start_pos.x(), 0)

        self.anim = QPropertyAnimation(self, b"pos", self)
        self.anim.setDuration(500)
        self.anim.setStartValue(start_pos)
        self.anim.setEndValue(end_pos)
        self.anim.finished.connect(self.hide)
        self.anim.start()


class MenuWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("منوی تنظیمات")
        self.setFixedSize(300, 200)

        self.background_label = QLabel(self)
        bg_pixmap = QPixmap("pic/v.webp").scaled(self.size())
        self.background_label.setPixmap(bg_pixmap)
        self.background_label.setGeometry(0, 0, 300, 200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        btn1 = QPushButton("گزینه اول")
        btn2 = QPushButton("گزینه دوم")
        btn3 = QPushButton("گزینه سوم")

        for btn in (btn1, btn2, btn3):
            btn.setFixedHeight(40)
            btn.setStyleSheet(
                "font-size: 16pt; color: white; background-color: rgba(0, 0, 0, 150);"
                "border: 2px solid white; border-radius: 10px;"
            )
            layout.addWidget(btn)

        btn1.clicked.connect(lambda: self.button_clicked("گزینه اول"))
        btn2.clicked.connect(lambda: self.button_clicked("گزینه دوم"))
        btn3.clicked.connect(lambda: self.button_clicked("گزینه سوم"))

        self.setLayout(layout)

    def button_clicked(self, text):
        print(f"{text} انتخاب شد")


class TimerThread(threading.Thread):
    def __init__(self, signal):
        super().__init__()
        self.signal = signal
        self._running = True
        self.seconds = 0

    def run(self):
        while self._running:
            time.sleep(1)
            self.seconds += 1
            minutes = self.seconds // 60
            secs = self.seconds % 60
            self.signal.emit(f"{minutes:02}:{secs:02}")

    def stop(self):
        self._running = False


class Calculator(QWidget):
    calculation_done = pyqtSignal(str)
    random_number_added = pyqtSignal(int)
    timer_updated = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ماشین حساب PyQt5")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(620, 800)

        # پس‌زمینه
        self.background_label = QLabel(self)
        bg_pixmap = QPixmap("pic/OIP.webp").scaled(self.size())
        self.background_label.setPixmap(bg_pixmap)
        self.background_label.setGeometry(0, 0, 620, 800)

        # تایمر
        self.timer_label = QLabel("00:00", self)
        self.timer_label.setGeometry(10, 10, 600, 40)
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 18pt; color: black; background: lightyellow; border: 2px solid gray; border-radius: 5px;")

        # ورودی
        self.entry = QLineEdit(self)
        self.entry.setGeometry(10, 60, 600, 40)
        self.entry.setAlignment(Qt.AlignLeft)
        self.entry.setStyleSheet(
            "font-size: 18pt; border: 2px solid gray; border-radius: 5px; background: white;"
        )

        # آیکون‌ها
        self.icon_normal = QIcon("pic/download-removebg-preview.png")
        self.icon_hover = QIcon("pic/v-removebg-preview.png")
        self.icon_pressed = QIcon("pic/p-removebg-preview.png")

        # دکمه‌ها با مختصات دستی
        self.buttons = {}
        button_definitions = [
            ('7', 10, 120), ('8', 100, 120), ('9', 190, 120), ('/', 280, 120),
            ('4', 10, 210), ('5', 100, 210), ('6', 190, 210), ('*', 280, 210),
            ('1', 10, 300), ('2', 100, 300), ('3', 190, 300), ('-', 280, 300),
            ('0', 10, 390), ('.', 100, 390), ('+', 190, 390), ('=', 280, 390),
            ('C', 10, 480), ('M', 100, 480), ('e', 190, 580),('r',280,580)
        ]

        for (text, x, y) in button_definitions:
            btn = QPushButton(text, self)
            btn.setGeometry(x, y, 80, 80)
            btn.setIcon(self.icon_normal)
            btn.setIconSize(QSize(60, 60))
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setStyleSheet("font-size: 20pt; color: white; border: none;")
            btn.installEventFilter(self)

            if text == '=':
                btn.clicked.connect(self.start_calculate_thread)
            elif text == 'C':
                btn.clicked.connect(self.clear)
            elif text == 'e':
                btn.clicked.connect(self.exit)
            elif text == 'M':
                btn.clicked.connect(self.open_menu_window)
            elif text == 'r':
                btn.clicked.connect(self.start_insert_random_thread)    
            else:
                btn.clicked.connect(lambda checked, t=text: self.press(t))

            self.buttons[btn] = text

        self.floating_msg = FloatingMessage(self)

        # سیگنال‌ها
        self.calculation_done.connect(self.on_calculation_done)
        self.random_number_added.connect(self.on_random_number_added)
        self.timer_updated.connect(self.update_timer_label)

        # تایمر در thread جدا
        self.timer_thread = TimerThread(self.timer_updated)
        self.timer_thread.start()

    def start_insert_random_thread(self):
        threading.Thread(target=self.insert_random_number, daemon=True).start()

    def insert_random_number(self):
        num = random.randint(0, 10)
        self.random_number_added.emit(num)

    def on_random_number_added(self, num):
        self.entry.setText(self.entry.text() + str(num))
        self.floating_msg.show_message(f"عدد تصادفی {num} اضافه شد")

    def start_calculate_thread(self):
        threading.Thread(target=self.calculate, daemon=True).start()

    def calculate(self):
        try:
            result = eval(self.entry.text())
            self.calculation_done.emit(str(result))
        except Exception:
            self.calculation_done.emit("خطا")

    def on_calculation_done(self, result):
        self.entry.setText(result)
        if result == "خطا":
            self.floating_msg.show_message("خطا در محاسبه")
        else:
            self.floating_msg.show_message("محاسبه انجام شد")

    def update_timer_label(self, text):
        self.timer_label.setText(text)

    def press(self, key):
        current_text = self.entry.text()
        self.entry.setText(current_text + key)
        self.floating_msg.show_message(f"دکمه {key} فشار داده شد")

    def clear(self):
        self.entry.clear()
        self.floating_msg.show_message("صفحه پاک شد")
        # تایمر رو ریست می‌کنیم:
        self.timer_thread.seconds = 0
        self.timer_label.setText("00:00")

    def exit(self):
        if hasattr(self, 'menu_window'):
            self.menu_window.close()
        self.timer_thread.stop()  # حتما thread تایمر رو متوقف کن
        self.close()

    def open_menu_window(self):
        self.menu_window = MenuWindow()
        self.menu_window.show()

    def eventFilter(self, source, event):
        if source in self.buttons:
            if event.type() == QEvent.Enter:
                source.setIcon(self.icon_hover)
            elif event.type() == QEvent.Leave:
                source.setIcon(self.icon_normal)
            elif event.type() == QEvent.MouseButtonPress:
                source.setIcon(self.icon_pressed)
            elif event.type() == QEvent.MouseButtonRelease:
                source.setIcon(self.icon_hover)
        return super().eventFilter(source, event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Calculator()
    window.show()
    sys.exit(app.exec_())
