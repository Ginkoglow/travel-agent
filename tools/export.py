from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from docx import Document
import os


def export_plan_to_pdf(content: str, filename: str = "旅行攻略.pdf") -> str:
    c = canvas.Canvas(filename, pagesize=A4)
    c.drawString(50, 800, "旅行智能助手 - 专属攻略")
    text_obj = c.beginText(50, 780)
    for line in content.split('\n'):
        text_obj.textLine(line)
    c.drawText(text_obj)
    c.save()
    return os.path.abspath(filename)


def export_to_pdf(content: str, filename: str = "旅行攻略.pdf"):
    """导出PDF"""
    c = canvas.Canvas(filename, pagesize=A4)
    c.drawString(50, 800, "旅行智能助手 - 专属攻略")
    text = c.beginText(50, 780)
    text.textLines(content)
    c.drawText(text)
    c.save()
    return os.path.abspath(filename)

def export_to_word(content: str, filename: str = "旅行攻略.docx"):
    """导出Word"""
    doc = Document()
    doc.add_heading('旅行智能助手 - 专属攻略', 0)
    doc.add_paragraph(content)
    doc.save(filename)
    return os.path.abspath(filename)