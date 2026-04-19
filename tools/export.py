import os
import re
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def _register_fonts():
    """尝试注册中文字体"""
    font_paths = [
        ('SimHei', 'C:/Windows/Fonts/simhei.ttf'),
        ('SimHei', '/System/Library/Fonts/STHeiti Light.ttc'),
        ('SimHei', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
    ]
    font_registered = False
    for font_name, font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont(font_name, font_path))
                addMapping(font_name, 0, 0, font_name)
                font_registered = True
                print(f"成功注册字体: {font_name} from {font_path}")
                break
            except Exception as e:
                print(f"注册字体 {font_name} 失败: {e}")
    return font_registered

def _clean_markdown(text: str) -> str:
    """移除或转换常见的 Markdown 符号，使纯文本更干净"""
    # 去除标题符号 ### 等
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # 去除粗体/斜体符号 ** 和 *
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'\*(.+?)\*', r'\1', text)
    # 去除列表符号 - 或 * 开头，保留缩进
    text = re.sub(r'^(\s*)[-*]\s+', r'\1• ', text, flags=re.MULTILINE)
    # 去除多余空行
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text

def export_plan_to_pdf(content: str, filename: str = None) -> str:
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    if filename is None:
        filename = f"travel_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(output_dir, filename)

    # 清理 Markdown 符号
    cleaned_content = _clean_markdown(content)

    # 创建文档模板，设置较大边距（1英寸 = 72磅）
    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        leftMargin=72,
        rightMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # 注册中文字体
    font_available = _register_fonts()
    font_name = "SimHei" if font_available else "Helvetica"

    # 样式表
    styles = getSampleStyleSheet()

    # 标题样式（居中、加粗）
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor='#2c3e50'
    )

    # 正文样式（左对齐，行距舒适）
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        leading=18,           # 行距
        alignment=TA_LEFT,
        spaceAfter=8,
        wordWrap='CJK'        # 中文字符换行优化
    )

    # 构建内容流
    story = []

    # 添加标题
    story.append(Paragraph("旅行智能助手 - 专属攻略", title_style))
    story.append(Spacer(1, 0.2 * inch))

    # 将文本按空行分割为段落，每个段落作为一个 Paragraph
    paragraphs = cleaned_content.split('\n\n')
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        # 将段落内部的换行转换为 <br/> 标签，保留手动换行
        para_html = para.replace('\n', '<br/>')
        story.append(Paragraph(para_html, body_style))

    # 生成 PDF
    doc.build(story)

    return os.path.abspath(filepath)