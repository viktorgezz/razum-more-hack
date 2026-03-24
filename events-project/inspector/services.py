from datetime import datetime
from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def _register_unicode_fonts() -> tuple[str, str]:
    regular_name = "DejaVuSans"
    bold_name = "DejaVuSans-Bold"
    regular_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    bold_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")

    if regular_path.exists() and regular_name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(regular_name, str(regular_path)))
    if bold_path.exists() and bold_name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(bold_name, str(bold_path)))

    if (
        regular_name in pdfmetrics.getRegisteredFontNames()
        and bold_name in pdfmetrics.getRegisteredFontNames()
    ):
        return regular_name, bold_name
    return "Helvetica", "Helvetica-Bold"


def generate_candidate_pdf(candidate, stats: dict, participations) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    regular_font, bold_font = _register_unicode_fonts()

    y = 800
    pdf.setFont(bold_font, 14)
    pdf.drawString(40, y, "Отчет по кандидату кадрового резерва")
    y -= 30

    pdf.setFont(regular_font, 11)
    pdf.drawString(40, y, f"Дата формирования: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    y -= 25
    pdf.drawString(40, y, f"ID: {candidate.id}")
    y -= 18
    pdf.drawString(40, y, f"Username: {candidate.username}")
    y -= 18
    pdf.drawString(40, y, f"Имя: {candidate.first_name} {candidate.last_name}")
    y -= 18
    pdf.drawString(40, y, f"Email: {candidate.email}")
    y -= 28

    pdf.setFont(bold_font, 12)
    pdf.drawString(40, y, "Ключевые показатели")
    y -= 20
    pdf.setFont(regular_font, 11)
    pdf.drawString(40, y, f"Участий в мероприятиях: {stats['events_count']}")
    y -= 18
    pdf.drawString(40, y, f"Подтверждено участий: {stats['confirmed_count']}")
    y -= 18
    pdf.drawString(40, y, f"Сумма баллов: {stats['total_points']}")
    y -= 18
    pdf.drawString(40, y, f"Средний балл: {stats['avg_points']}")
    y -= 28

    pdf.setFont(bold_font, 12)
    pdf.drawString(40, y, "Последние участия")
    y -= 20
    pdf.setFont(regular_font, 10)
    for part in participations[:10]:
        line = (
            f"- {part.event.name[:45]} | {part.event.event_date.strftime('%Y-%m-%d')} "
            f"| статус: {part.status} | баллы: {part.points_awarded}"
        )
        pdf.drawString(40, y, line)
        y -= 15
        if y < 50:
            pdf.showPage()
            y = 800
            pdf.setFont(regular_font, 10)

    pdf.showPage()
    pdf.save()
    return buffer.getvalue()
