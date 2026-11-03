"""Графический интерфейс PostalService на PySide6."""
import sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QComboBox, QDoubleSpinBox, QFormLayout, QFrame,
    QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMainWindow, QMessageBox,
    QPushButton, QTabWidget, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QWidget, QHeaderView,
)
from postal_service import Letter, Bandrol, Parcel, DeliveryCalculator
from postal_service import DeliveryType, PostalRepository
from report_export import export_to_docx

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "data" / "postal_history.db"
REPORT_PATH = APP_DIR / "postal_report.docx"


class PostalServiceWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PostalService — управление отправлениями")
        self.resize(1120, 760)
        self.setMinimumSize(940, 650)
        self.repository = PostalRepository(DB_PATH)
        self._build_ui()
        self._apply_style()
        self.refresh_history()

    def _build_ui(self):
        root = QWidget()
        outer = QVBoxLayout(root)
        outer.setContentsMargins(28, 22, 28, 24)
        outer.setSpacing(18)
        header = QHBoxLayout()
        brand = QVBoxLayout()
        eyebrow = QLabel("POSTAL OPERATIONS")
        eyebrow.setObjectName("eyebrow")
        title = QLabel("Почтовые отправления")
        title.setObjectName("pageTitle")
        subtitle = QLabel("Расчёт тарифов, история операций и экспорт отчётов")
        subtitle.setObjectName("subtitle")
        brand.addWidget(eyebrow)
        brand.addWidget(title)
        brand.addWidget(subtitle)
        header.addLayout(brand)
        header.addStretch()
        badge = QLabel("●  БАЗА ДАННЫХ ПОДКЛЮЧЕНА")
        badge.setObjectName("statusBadge")
        header.addWidget(badge, alignment=Qt.AlignTop)
        outer.addLayout(header)
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_calculation_tab(), "  Новый расчёт  ")
        self.tabs.addTab(self._create_history_tab(), "  История отправлений  ")
        outer.addWidget(self.tabs)
        footer = QLabel("PostalService  •  Учебная модель тарифов  •  SQLite")
        footer.setObjectName("footer")
        outer.addWidget(footer)
        self.setCentralWidget(root)

    @staticmethod
    def _number(minimum, maximum, value, suffix="", decimals=2):
        field = QDoubleSpinBox()
        field.setRange(minimum, maximum)
        field.setValue(value)
        field.setDecimals(decimals)
        field.setSuffix(suffix)
        field.setKeyboardTracking(False)
        return field

    def _create_calculation_tab(self):
        page = QWidget()
        layout = QGridLayout(page)
        layout.setContentsMargins(4, 20, 4, 4)
        layout.setHorizontalSpacing(18)
        card = QFrame()
        card.setObjectName("card")
        form_layout = QVBoxLayout(card)
        form_layout.setContentsMargins(22, 22, 22, 22)
        form_layout.setSpacing(15)
        section_title = QLabel("Параметры отправления")
        section_title.setObjectName("sectionTitle")
        hint = QLabel("Заполните данные отправителя, получателя и отправления.")
        hint.setObjectName("muted")
        form_layout.addWidget(section_title)
        form_layout.addWidget(hint)
        form = QFormLayout()
        form.setVerticalSpacing(12)
        form.setHorizontalSpacing(18)
        self.category = QComboBox()
        self.category.addItems(["Письмо", "Бандероль", "Посылка"])
        self.sender = QLineEdit()
        self.sender.setPlaceholderText("Например, Артём")
        self.recipient = QLineEdit()
        self.recipient.setPlaceholderText("Например, Максим")
        self.distance = self._number(1, 100000, 100, " км", 1)
        self.weight = self._number(0.01, 10000, 1, " кг", 2)
        self.length = self._number(0.1, 10000, 20, " см", 1)
        self.width = self._number(0.1, 10000, 15, " см", 1)
        self.height = self._number(0.1, 10000, 10, " см", 1)
        self.delivery = QComboBox()
        self.delivery.addItem("Стандартная · 5 дней", "STANDARD")
        self.delivery.addItem("Экспресс · 2 дня", "EXPRESS")
        self.delivery.addItem("Экономичная · 9 дней", "ECONOMY")
        for label, widget in [
            ("Тип отправления", self.category), ("Отправитель", self.sender),
            ("Получатель", self.recipient), ("Расстояние", self.distance),
            ("Фактический вес", self.weight), ("Длина", self.length),
            ("Ширина", self.width), ("Высота", self.height),
            ("Тип доставки", self.delivery),
        ]:
            form.addRow(label, widget)
        form_layout.addLayout(form)
        calculate = QPushButton("Рассчитать стоимость  →")
        calculate.setObjectName("primaryButton")
        calculate.clicked.connect(self.calculate)
        form_layout.addWidget(calculate)

        result_card = QFrame()
        result_card.setObjectName("resultCard")
        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(24, 24, 24, 24)
        result_layout.setSpacing(13)
        result_label = QLabel("РЕЗУЛЬТАТ РАСЧЁТА")
        result_label.setObjectName("eyebrow")
        self.result_price = QLabel("— ₽")
        self.result_price.setObjectName("price")
        self.result_description = QLabel("Заполните форму и выполните расчёт.")
        self.result_description.setObjectName("resultDescription")
        self.result_description.setWordWrap(True)
        self.result_details = QLabel("")
        self.result_details.setObjectName("resultDetails")
        self.result_details.setWordWrap(True)
        result_layout.addWidget(result_label)
        result_layout.addSpacing(10)
        result_layout.addWidget(self.result_price)
        result_layout.addWidget(self.result_description)
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setObjectName("separator")
        result_layout.addWidget(separator)
        result_layout.addWidget(self.result_details)
        result_layout.addStretch()
        export = QPushButton("Экспортировать историю в DOCX")
        export.setObjectName("secondaryButton")
        export.clicked.connect(self.export_report)
        result_layout.addWidget(export)
        layout.addWidget(card, 0, 0)
        layout.addWidget(result_card, 0, 1)
        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 2)
        return page

    def _create_history_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(4, 20, 4, 4)
        layout.setSpacing(14)
        top = QHBoxLayout()
        labels = QVBoxLayout()
        title = QLabel("История расчётов")
        title.setObjectName("sectionTitle")
        hint = QLabel("Все операции, сохранённые в локальной базе SQLite.")
        hint.setObjectName("muted")
        labels.addWidget(title)
        labels.addWidget(hint)
        top.addLayout(labels)
        top.addStretch()
        refresh = QPushButton("Обновить")
        refresh.setObjectName("secondaryButton")
        refresh.clicked.connect(self.refresh_history)
        export = QPushButton("Экспорт DOCX")
        export.setObjectName("primarySmall")
        export.clicked.connect(self.export_report)
        top.addWidget(refresh)
        top.addWidget(export)
        layout.addLayout(top)
        self.history_table = QTableWidget(0, 8)
        self.history_table.setHorizontalHeaderLabels([
            "ID", "Дата", "Тип", "Отправитель", "Получатель",
            "Расстояние", "Доставка", "Стоимость"
        ])
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setSelectionMode(QTableWidget.SingleSelection)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.history_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.history_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.history_table.setObjectName("historyTable")
        layout.addWidget(self.history_table)
        self.history_count = QLabel("Записей: 0")
        self.history_count.setObjectName("muted")
        layout.addWidget(self.history_count)
        return page

    def calculate(self):
        classes = {"Письмо": Letter, "Бандероль": Bandrol, "Посылка": Parcel}
        delivery_types = {
            "STANDARD": DeliveryType.STANDARD,
            "EXPRESS": DeliveryType.EXPRESS,
            "ECONOMY": DeliveryType.ECONOMY,
        }
        try:
            item = classes[self.category.currentText()](
                self.sender.text().strip() or "Не указан",
                self.recipient.text().strip() or "Не указан",
                self.distance.value(), self.weight.value(), self.length.value(),
                self.width.value(), self.height.value(),
            )
            result = DeliveryCalculator(item, delivery_types[self.delivery.currentData()]).calculate()
            record_id = self.repository.save(result)
            self.result_price.setText(f'{result["total"]:,.2f} ₽'.replace(",", " "))
            self.result_description.setText(f'{result["category"]} · {result["delivery_type"].lower()}')
            self.result_details.setText(
                f'Отправитель: {result["sender"]}\nПолучатель: {result["recipient"]}\n'
                f'Расчётный вес: {result["chargeable_weight_kg"]:.2f} кг\n'
                f'Объём: {result["volume_cm3"]:.0f} см³\n'
                f'Срок доставки: {result["delivery_days"]} дн.\n'
                f'Запись №{record_id} сохранена в SQLite.'
            )
            self.refresh_history()
            QMessageBox.information(self, "Расчёт выполнен", f'Стоимость: {result["total"]:.2f} ₽\nЗапись №{record_id} сохранена.')
        except (ValueError, TypeError, KeyError) as error:
            QMessageBox.warning(self, "Не удалось выполнить расчёт", str(error))

    def refresh_history(self):
        rows = self.repository.get_all()
        self.history_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            values = [row["id"], row["created_at"], row["category"], row["sender"],
                      row["recipient"], f'{row["distance_km"]:.1f} км',
                      row["delivery_type"], f'{row["total"]:.2f} ₽']
            for c, value in enumerate(values):
                cell = QTableWidgetItem(str(value))
                if c in (0, 5, 7):
                    cell.setTextAlignment(Qt.AlignCenter)
                self.history_table.setItem(r, c, cell)
        self.history_count.setText(f"Записей: {len(rows)}")

    def export_report(self):
        try:
            path = export_to_docx(self.repository.get_all(), str(REPORT_PATH))
            QMessageBox.information(self, "Экспорт завершён", f"Отчёт сохранён:\n{path}")
        except Exception as error:
            QMessageBox.critical(self, "Ошибка экспорта", str(error))

    def _apply_style(self):
        self.setStyleSheet("""
            QMainWindow, QWidget { background:#f3f6fb; color:#172033; font-family:'Segoe UI'; font-size:10pt; }
            QLabel#eyebrow { color:#64748b; font-size:8pt; font-weight:700; }
            QLabel#pageTitle { color:#111827; font-size:25pt; font-weight:750; }
            QLabel#subtitle, QLabel#muted, QLabel#footer { color:#718096; font-size:9pt; }
            QLabel#statusBadge { color:#087f5b; background:#dff7ed; border-radius:12px; padding:9px 13px; font-size:8pt; font-weight:700; }
            QTabWidget::pane { border:0; background:transparent; }
            QTabBar::tab { background:transparent; color:#64748b; padding:12px 18px; margin-right:6px; font-weight:600; border-bottom:2px solid transparent; }
            QTabBar::tab:selected { color:#2457d6; border-bottom:2px solid #2457d6; }
            QFrame#card {
                background:#fff;
                border:1px solid #e4eaf2;
                border-radius:16px;
            }

            QFrame#resultCard {
                background:#172b4d;
                border:0;
                border-radius:16px;
            }

            QFrame#resultCard QWidget {
                background:transparent;
                color:#edf4ff;
            }

            QFrame#resultCard QLabel {
                background:transparent;
                color:#dce8f8;
            }
            QLabel#sectionTitle { color:#172033; font-size:15pt; font-weight:700; }
            QFrame#resultCard QLabel#eyebrow { color:#a9bddb; }
            QLabel#price { color:#fff; font-size:29pt; font-weight:750; }
            QLabel#resultDescription { color:#d8e4f5; font-size:11pt; font-weight:600; }
            QLabel#resultDetails { color:#c0cee1; font-size:10pt; }
            QLineEdit, QComboBox, QDoubleSpinBox { background:#f8fafc; border:1px solid #dbe3ee; border-radius:8px; padding:9px 10px; min-height:20px; }
            QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus { border:1px solid #4777e8; background:#fff; }
            QPushButton { border-radius:9px; padding:10px 15px; font-weight:650; min-height:20px; }
            QPushButton#primaryButton, QPushButton#primarySmall { background:#2859d8; color:#fff; border:0; }
            QPushButton#primaryButton:hover, QPushButton#primarySmall:hover { background:#1f49b7; }
            QPushButton#secondaryButton { background:#edf2f8; color:#26364d; border:1px solid #dce4ef; }
            QFrame#resultCard QPushButton#secondaryButton { background:#29456c; color:#fff; border:1px solid #456184; }
            QTableWidget#historyTable { background:#fff; alternate-background-color:#f7f9fc; border:1px solid #e4eaf2; border-radius:12px; gridline-color:#edf1f6; selection-background-color:#dce8ff; selection-color:#172033; }
            QHeaderView::section { background:#f0f4f9; color:#52627a; border:0; border-bottom:1px solid #e0e7f0; padding:11px 8px; font-weight:700; }
        """)


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = PostalServiceWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
