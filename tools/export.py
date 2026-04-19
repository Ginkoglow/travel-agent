import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

def export_plan_to_pdf(content: str, filename: str = None) -> str:
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    if filename is None:
        filename = f"travel_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(output_dir, filename)

    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "旅行智能助手 - 专属攻略")
    c.line(50, height - 55, width - 50, height - 55)
    c.setFont("Helvetica", 11)
    y = height - 80
    for line in content.split('\n'):
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = height - 50
        wrapped = simpleSplit(line, "Helvetica", 11, width - 100)
        for wline in wrapped:
            c.drawString(50, y, wline)
            y -= 16
        y -= 5
    c.save()
    return os.path.abspath(filepath)