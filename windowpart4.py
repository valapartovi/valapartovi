import sys
import math
import random
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QMessageBox, QGridLayout, QGroupBox,
    QSizePolicy, QScrollArea, QHBoxLayout
)
from PyQt6.QtGui import QIntValidator, QMouseEvent, QFont, QDrag, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QByteArray, QMimeData
from reportlab.pdfgen import canvas


class PageWidget(QGroupBox):
    double_clicked = pyqtSignal(object)
    dragged = pyqtSignal(int, int)

    def __init__(self, index, close_callback):
        super().__init__(f"صفحه {index + 1}")
        self.index = index
        self.close_callback = close_callback
        self.setAcceptDrops(True)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.main_layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        self.label = QLabel(f"این صفحه شماره {index + 1} است")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.label)

        self.btn_close = QPushButton("بستن صفحه")
        self.btn_close.setFixedWidth(100)
        self.btn_close.clicked.connect(self.close_page)
        header_layout.addWidget(self.btn_close)

        self.main_layout.addLayout(header_layout)

        # Content: x, y, z rows with values
        self.value_labels = {}
        font = QFont()
        font.setPointSize(24)  # بزرگ کردن فونت

        for key in ['x', 'y', 'z']:
            row = QHBoxLayout()
            label = QLabel(key)
            label.setFont(font)
            row.addWidget(label)

            value_label = QLabel("0")
            value_label.setFont(font)
            row.addWidget(value_label)

            self.value_labels[key] = value_label
            self.main_layout.addLayout(row)

        # دکمه ساخت PDF
        self.btn_pdf = QPushButton("ساخت PDF")
        self.btn_pdf.clicked.connect(self.create_pdf)
        self.main_layout.addWidget(self.btn_pdf)

        self.setLayout(self.main_layout)

        # Timer for updating values every 2 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_random_values)
        self.timer.start(2000)

        # تنظیم اولیه استایل کادرها (تم روشن)
        self.set_number_box_style(False)

    def set_number_box_style(self, dark_mode: bool):
        border_color = "#888888" if not dark_mode else "#FFFFFF"  # خاکستری برای تم روشن، سفید برای تم تاریک
        text_color = "#000000" if not dark_mode else "#FFFFFF"
        for label in self.value_labels.values():
            label.setStyleSheet(f"""
                border: 2px solid {border_color};
                border-radius: 4px;
                padding: 5px;
                background-color: transparent;
                color: {text_color};
            """)

        # همینطور عنوان و دکمه‌ها را هم تغییر بده
        self.setStyleSheet(f"""
            QGroupBox {{
                color: {text_color};
                border: 2px solid {border_color};
                border-radius: 5px;
                margin-top: 2ex;
                background-color: {'#222222' if dark_mode else '#f0f0f0'};
            }}
            QPushButton {{
                background-color: {'#444444' if dark_mode else '#ddd'};
                color: {text_color};
                border-radius: 4px;
                padding: 6px;
            }}
            QPushButton:hover {{
                background-color: {'#555555' if dark_mode else '#ccc'};
            }}
            QLabel {{
                color: {text_color};
            }}
        """)

    def close_page(self):
        self.timer.stop()
        self.close_callback(self)

    def update_index(self, new_index):
        self.index = new_index
        self.setTitle(f"صفحه {new_index + 1}")
        self.label.setText(f"این صفحه شماره {new_index + 1} است")

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self.double_clicked.emit(self)
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setData("application/x-page-index", QByteArray(str(self.index).encode()))
            drag.setMimeData(mime_data)

            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())

            drag.exec()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-page-index"):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        from_index_data = event.mimeData().data("application/x-page-index")
        from_index = int(bytes(from_index_data).decode())
        to_index = self.index
        if from_index != to_index:
            self.dragged.emit(from_index, to_index)
        event.acceptProposedAction()

    def update_random_values(self):
        for key in self.value_labels:
            self.value_labels[key].setText(str(random.randint(1, 10)))

    def create_pdf(self):
        filename = f"page_{self.index + 1}.pdf"

        c = canvas.Canvas(filename)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, 800, f"محتوای صفحه شماره {self.index + 1}")

        y = 750
        c.setFont("Helvetica", 14)
        for key, label in self.value_labels.items():
            text = f"{key} = {label.text()}"
            c.drawString(100, y, text)
            y -= 30

        c.save()

        try:
            if sys.platform.startswith('darwin'):
                subprocess.call(('open', filename))
            elif sys.platform.startswith('linux'):
                subprocess.call(('xdg-open', filename))
            elif sys.platform.startswith('win'):
                os.startfile(filename)
            else:
                QMessageBox.information(self, "اطلاع", f"PDF ذخیره شد: {filename}")
        except Exception as e:
            QMessageBox.warning(self, "خطا", f"امکان باز کردن فایل وجود ندارد.\n{e}")


class CalculatorWidget(QWidget):
    double_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setFixedHeight(250)  # ارتفاع ثابت برای ماشین حساب (می‌توانید تغییر دهید)

        layout = QVBoxLayout()

        self.display = QLineEdit()
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setReadOnly(True)
        self.display.setFixedHeight(40)
        layout.addWidget(self.display)

        buttons_layout = QGridLayout()

        buttons = [
            ('7', 0, 0, 1, 1), ('8', 0, 1, 1, 1), ('9', 0, 2, 1, 1), ('/', 0, 3, 1, 1),
            ('4', 1, 0, 1, 1), ('5', 1, 1, 1, 1), ('6', 1, 2, 1, 1), ('*', 1, 3, 1, 1),
            ('1', 2, 0, 1, 1), ('2', 2, 1, 1, 1), ('3', 2, 2, 1, 1), ('-', 2, 3, 1, 1),
            ('0', 3, 0, 1, 1), ('.', 3, 1, 1, 1), ('C', 3, 2, 1, 1), ('+', 3, 3, 1, 1),
            ('=', 4, 0, 1, 4)
        ]

        for text, row, col, rowspan, colspan in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(self.on_button_clicked)
            buttons_layout.addWidget(btn, row, col, rowspan, colspan)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def mouseDoubleClickEvent(self, event):
        self.double_clicked.emit()

    def on_button_clicked(self):
        sender = self.sender()
        text = sender.text()

        if text == 'C':
            self.display.clear()
        elif text == '=':
            try:
                result = str(eval(self.display.text()))
                self.display.setText(result)
            except Exception:
                self.display.setText("خطا")
        else:
            self.display.setText(self.display.text() + text)


class CalculatorPage(QGroupBox):
    double_clicked = pyqtSignal(object)
    dragged = pyqtSignal(int, int)

    def __init__(self, index, close_callback):
        super().__init__("ماشین حساب")
        self.index = index
        self.close_callback = close_callback
        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.main_layout = QVBoxLayout()

        self.calculator = CalculatorWidget()
        self.main_layout.addWidget(self.calculator)

        

        self.setLayout(self.main_layout)

        # برای تم تاریک استایل می‌گذاریم
        self.set_number_box_style(False)

    def set_number_box_style(self, dark_mode: bool):
        border_color = "#888888" if not dark_mode else "#FFFFFF"
        text_color = "#000000" if not dark_mode else "#FFFFFF"
        self.setStyleSheet(f"""
            QGroupBox {{
                color: {text_color};
                border: 2px solid {border_color};
                border-radius: 5px;
                margin-top: 2ex;
                background-color: {'#222222' if dark_mode else '#f0f0f0'};
            }}
            QPushButton {{
                background-color: {'#444444' if dark_mode else '#ddd'};
                color: {text_color};
                border-radius: 4px;
                padding: 6px;
            }}
            QPushButton:hover {{
                background-color: {'#555555' if dark_mode else '#ccc'};
            }}
            QLabel {{
                color: {text_color};
            }}
        """)

    def update_index(self, new_index):
        self.index = new_index
        self.setTitle("ماشین حساب")  # عنوان ثابت

    def mouseDoubleClickEvent(self, event):
        self.double_clicked.emit(self)
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setData("application/x-page-index", QByteArray(str(self.index).encode()))
            drag.setMimeData(mime_data)

            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)
            drag.setHotSpot(event.pos())

            drag.exec()

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("application/x-page-index"):
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        from_index_data = event.mimeData().data("application/x-page-index")
        from_index = int(bytes(from_index_data).decode())
        to_index = self.index
        if from_index != to_index:
            self.dragged.emit(from_index, to_index)
        event.acceptProposedAction()


class MainWindow(QWidget):
    MAX_PAGES = 16

    def __init__(self):
        super().__init__()

        self.setWindowTitle("پنجره اصلی با صفحات شبکه‌ای")
        self.resize(1700, 900)

        self.pages = []
        self.maximized_page = None

        self.dark_mode = False
        self.calculator_page = None

        main_layout = QVBoxLayout()

        # ورودی و دکمه‌ها (که بعدا مخفی می‌شوند)
        self.input_layout = QHBoxLayout()
        self.label = QLabel("تعداد صفحات را وارد کنید (1 تا 16):")
        self.input_layout.addWidget(self.label)

        self.input = QLineEdit()
        self.input.setValidator(QIntValidator(1, self.MAX_PAGES))
        self.input_layout.addWidget(self.input)

        self.btn_create = QPushButton("ایجاد صفحات")
        self.btn_create.clicked.connect(self.create_pages)
        self.input_layout.addWidget(self.btn_create)

        # دکمه تم تاریک/روشن
        self.btn_toggle_theme = QPushButton("تم تاریک / روشن")
        self.btn_toggle_theme.clicked.connect(self.toggle_theme)
        self.input_layout.addWidget(self.btn_toggle_theme)

        self.btn_exit = QPushButton("خروج")
        self.btn_exit.clicked.connect(self.close)
        self.input_layout.addWidget(self.btn_exit)

        main_layout.addLayout(self.input_layout)

        self.control_layout = QHBoxLayout()
        self.control_layout.setSpacing(20)

        self.btn_add_page = QPushButton("اضافه کردن صفحه")
        self.btn_add_page.clicked.connect(self.add_page)
        self.control_layout.addWidget(self.btn_add_page, alignment=Qt.AlignmentFlag.AlignLeft)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.control_layout.addWidget(spacer)

        self.btn_close_all = QPushButton("بستن همه صفحات")
        self.btn_close_all.clicked.connect(self.close_all_pages)
        self.control_layout.addWidget(self.btn_close_all, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.addLayout(self.control_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.scroll_area)

        self.container = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        self.container.setLayout(self.grid_layout)

        self.scroll_area.setWidget(self.container)

        self.setLayout(main_layout)

        self.btn_add_page.hide()
        self.btn_close_all.hide()

    def create_pages(self):
        n_text = self.input.text()
        if not n_text:
            QMessageBox.warning(self, "خطا", "لطفا تعداد صفحات را وارد کنید.")
            return

        n = int(n_text)
        if n < 1 or n > self.MAX_PAGES:
            QMessageBox.warning(self, "خطا", f"تعداد صفحات باید بین 1 تا {self.MAX_PAGES} باشد.")
            return

        self.close_all_pages()

        for i in range(n):
            page = PageWidget(i, self.close_page)
            page.double_clicked.connect(self.maximize_page)
            page.dragged.connect(self.reorder_pages)
            self.pages.append(page)

        # اضافه کردن ماشین حساب در آخر
        self.calculator_page = CalculatorPage(len(self.pages), self.close_page)
        self.calculator_page.double_clicked.connect(self.maximize_page)
        self.calculator_page.dragged.connect(self.reorder_pages)
        self.pages.append(self.calculator_page)

        self.refresh_grid()

        # بعد از ساخت صفحات، ورودی و دکمه‌های ایجاد مخفی شود
        self.input.hide()
        self.btn_create.hide()
        self.label.hide()

        # نمایش دکمه‌های کنترل صفحات
        self.btn_add_page.show()
        self.btn_close_all.show()

    def refresh_grid(self):
        # حذف همه ویجت‌ها از شبکه
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                self.grid_layout.removeWidget(widget)
                widget.setParent(None)

        count = len(self.pages)
        if count == 0:
            return

        cols = math.ceil(math.sqrt(count))
        rows = math.ceil(count / cols)

        # اضافه کردن صفحات به شبکه
        for index, page in enumerate(self.pages):
            page.update_index(index)
            # فقط اگر صفحه متد set_number_box_style داشت، صدا بزن
            if hasattr(page, 'set_number_box_style'):
                page.set_number_box_style(self.dark_mode)
            self.grid_layout.addWidget(page, index // cols, index % cols)

        self.scroll_area.update()
        self.container.update()

    def close_page(self, page):
        if page in self.pages:
            self.pages.remove(page)
            page.deleteLater()
            if page == self.calculator_page:
                self.calculator_page = None
            self.refresh_grid()

    def close_all_pages(self):
        for page in self.pages:
            page.deleteLater()
        self.pages.clear()
        self.calculator_page = None
        self.refresh_grid()

        # ورودی و دکمه‌ها را دوباره نمایش بده
        self.input.show()
        self.btn_create.show()
        self.label.show()

        self.btn_add_page.hide()
        self.btn_close_all.hide()

    def add_page(self):
        if len(self.pages) >= self.MAX_PAGES:
            QMessageBox.warning(self, "خطا", f"حداکثر تعداد صفحات {self.MAX_PAGES} است.")
            return

        # صفحه جدید
        page = PageWidget(len(self.pages), self.close_page)
        page.double_clicked.connect(self.maximize_page)
        page.dragged.connect(self.reorder_pages)

        # اگر ماشین حساب وجود دارد، صفحه جدید را قبل از آن اضافه کنیم
        if self.calculator_page:
            self.pages.insert(len(self.pages) - 1, page)
        else:
            self.pages.append(page)

        self.refresh_grid()

    def maximize_page(self, page):
        if self.maximized_page is None:
            self.maximized_page = page
            # مخفی کردن بقیه صفحات
            for p in self.pages:
                if p != page:
                    p.hide()

        # صفحه بزرگ شده را در سطر اول و ستون اول قرار بده و بزرگش کن
            self.grid_layout.addWidget(page, 0, 0, 1, self.grid_layout.columnCount())
            page.show()
        else:
        # بازگرداندن همه صفحات به حالت عادی
            self.maximized_page = None
            for p in self.pages:
                p.show()
            self.refresh_grid()


    def reorder_pages(self, from_index, to_index):
        if from_index < 0 or from_index >= len(self.pages) or to_index < 0 or to_index >= len(self.pages):
            return
        page = self.pages.pop(from_index)
        self.pages.insert(to_index, page)
        self.refresh_grid()

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode

        # تغییر استایل کلی پنجره
        if self.dark_mode:
            self.setStyleSheet("""
                QWidget {
                    background-color: #222222;
                    color: white;
                }
                QLineEdit, QTextEdit {
                    background-color: #444444;
                    color: white;
                    border: 1px solid #666666;
                }
                QPushButton {
                    background-color: #444444;
                    color: white;
                    border-radius: 6px;
                    padding: 6px;
                }
                QPushButton:hover {
                    background-color: #555555;
                }
            """)
        else:
            self.setStyleSheet("")

        # تغییر استایل صفحات
        for page in self.pages:
            if hasattr(page, 'set_number_box_style'):
                page.set_number_box_style(self.dark_mode)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
