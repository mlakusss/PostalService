"""Экспорт истории расчётов в документ DOCX."""
from docx import Document
from docx.shared import Pt


def export_to_docx(rows, path="postal_report.docx"):
    document = Document()
    document.add_heading("Отчёт о почтовых отправлениях", 0)
    document.add_paragraph("Сформировано приложением PostalService.")
    if not rows:
        document.add_paragraph("Записей пока нет.")
    else:
        table = document.add_table(rows=1, cols=8)
        table.style = "Table Grid"
        headers = ["ID", "Дата", "Тип", "Отправитель", "Получатель",
                   "Расстояние, км", "Доставка", "Цена"]
        for cell, value in zip(table.rows[0].cells, headers):
            cell.text = value
        for row in rows:
            cells = table.add_row().cells
            values = [
                row["id"], row["created_at"], row["category"],
                row["sender"], row["recipient"], row["distance_km"],
                row["delivery_type"], f'{row["total"]:.2f}'
            ]
            for cell, value in zip(cells, values):
                cell.text = str(value)
    document.add_paragraph(
        "Примечание: тарифы являются учебной моделью и могут быть изменены "
        "в константах DeliveryCalculator."
    )
    document.save(path)
    return path
