import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QMessageBox, QGridLayout, QTextEdit, QGroupBox,
    QSizePolicy, QScrollArea, QHBoxLayout
)
from PyQt6.QtGui import QIntValidator, QMouseEvent
from PyQt6.QtCore import Qt, pyqtSignal

class PageWidget(QGroupBox):
    double_clicked = pyqtSignal(object)

    def __init__(self, index, close_callback):
        super().__init__(f"صفحه {index + 1}")
        self.close_callback = close_callback
        self.is_maximized = False

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        main_layout = QVBoxLayout()

        # هدر صفحه شامل عنوان و دکمه بستن
        header_layout = QHBoxLayout()
        self.label = QLabel(f"این صفحه شماره {index + 1} است")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.label)

        self.btn_close = QPushButton("بستن صفحه")
        self.btn_close.setFixedWidth(100)
        self.btn_close.clicked.connect(self.close_page)
        header_layout.addWidget(self.btn_close)

        main_layout.addLayout(header_layout)

        # لایه افقی فقط شامل QTextEdit بدون ستون لیبل‌های x,y,z
        content_layout = QHBoxLayout()
        # گروه با عنوان "متن صفحه"
        text_group = QGroupBox("متن صفحه")
        text_layout = QVBoxLayout()
        self.text_edit = QTextEdit()
        # متن با خطوط خالی بین حروف برای فاصله بیشتر عمودی
        self.text_edit.setText("x\n\ny\n\nz")
        self.text_edit.setPlaceholderText(f"متن صفحه {index + 1}")
        text_layout.addWidget(self.text_edit)
        text_group.setLayout(text_layout)

        content_layout.addWidget(text_group)

        main_layout.addLayout(content_layout)

        self.setLayout(main_layout)

    def close_page(self):
        self.close_callback(self)

    def update_index(self, new_index):
        self.setTitle(f"صفحه {new_index + 1}")
        self.label.setText(f"این صفحه شماره {new_index + 1} است")
        self.text_edit.setPlaceholderText(f"متن صفحه {new_index + 1}")

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self.double_clicked.emit(self)
        event.accept()

class MainWindow(QWidget):
    MAX_PAGES = 16

    def __init__(self):
        super().__init__()

        self.setWindowTitle("پنجره اصلی با صفحات شبکه‌ای")
        self.resize(1100, 800)

        self.pages = []
        self.maximized_page = None

        main_layout = QVBoxLayout()

        self.input_layout = QHBoxLayout()
        self.label = QLabel("تعداد صفحات را وارد کنید (1 تا 16):")
        self.input_layout.addWidget(self.label)

        self.input = QLineEdit()
        self.input.setValidator(QIntValidator(1, self.MAX_PAGES))
        self.input_layout.addWidget(self.input)

        self.btn_create = QPushButton("ایجاد صفحات")
        self.btn_create.clicked.connect(self.create_pages)
        self.input_layout.addWidget(self.btn_create)

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

        self.btn_add_page.hide()
        self.btn_close_all.hide()

        main_layout.addLayout(self.control_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.pages_container = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        self.pages_container.setLayout(self.grid_layout)

        self.scroll_area.setWidget(self.pages_container)
        main_layout.addWidget(self.scroll_area)

        self.setLayout(main_layout)

    def create_pages(self):
        text = self.input.text()
        if not text:
            QMessageBox.warning(self, "خطا", "لطفاً تعداد صفحات را وارد کنید.")
            return

        n = int(text)
        if n < 1 or n > self.MAX_PAGES:
            QMessageBox.warning(self, "خطا", f"تعداد صفحات باید بین 1 تا {self.MAX_PAGES} باشد.")
            return

        self.pages.clear()
        self.clear_grid()

        for i in range(n):
            page = PageWidget(i, self.close_page)
            page.double_clicked.connect(self.toggle_maximize_page)
            self.pages.append(page)

        self.arrange_pages()

        self.label.hide()
        self.input.hide()
        self.btn_create.hide()
        self.btn_exit.hide()

        self.btn_add_page.show()
        self.btn_close_all.show()

    def arrange_pages(self):
        if self.maximized_page is not None:
            self.clear_grid()
            self.grid_layout.addWidget(self.maximized_page, 0, 0)
            return

        n = len(self.pages)
        if n == 0:
            return

        cols = math.ceil(math.sqrt(n))
        rows = math.ceil(n / cols)

        self.clear_grid()

        for i, page in enumerate(self.pages):
            page.update_index(i)
            row = i // cols
            col = i % cols
            self.grid_layout.addWidget(page, row, col)

    def clear_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)

    def add_page(self):
        if len(self.pages) >= self.MAX_PAGES:
            QMessageBox.warning(self, "هشدار", f"حداکثر تعداد صفحات ({self.MAX_PAGES}) ایجاد شده است.")
            return

        new_index = len(self.pages)
        page = PageWidget(new_index, self.close_page)
        page.double_clicked.connect(self.toggle_maximize_page)
        self.pages.append(page)

        self.arrange_pages()

    def close_page(self, page):
        if page in self.pages:
            self.pages.remove(page)
            if self.maximized_page == page:
                self.maximized_page = None
            page.setParent(None)
            self.arrange_pages()

            if len(self.pages) == 0:
                self.btn_add_page.hide()
                self.btn_close_all.hide()
                self.label.show()
                self.input.show()
                self.btn_create.show()
                self.btn_exit.show()

    def close_all_pages(self):
        for page in self.pages:
            page.setParent(None)
        self.pages.clear()
        self.maximized_page = None
        self.clear_grid()

        self.btn_add_page.hide()
        self.btn_close_all.hide()
        self.label.show()
        self.input.show()
        self.btn_create.show()
        self.btn_exit.show()

    def toggle_maximize_page(self, page):
        if self.maximized_page == page:
            self.maximized_page = None
        else:
            self.maximized_page = page
        self.arrange_pages()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())
