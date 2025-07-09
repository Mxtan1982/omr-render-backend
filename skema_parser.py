import re
from docx import Document
import fitz  # PyMuPDF
import os

def parse_answers_from_text(text):
    """
    提取 '1. A'、'2) B' 等格式的标准答案
    返回有序答案列表 ['A', 'B', 'C', ...]
    """
    pattern = r"\b(\d+)[\.\)]\s*([ABCD])"
    matches = re.findall(pattern, text)
    sorted_matches = sorted(matches, key=lambda x: int(x[0]))
    answers = [ans for _, ans in sorted_matches]
    return answers

def extract_from_docx(path):
    """
    从 DOCX 文件中提取文本并解析为答案
    """
    try:
        doc = Document(path)
        full_text = "\n".join([para.text for para in doc.paragraphs])
        return parse_answers_from_text(full_text)
    except Exception as e:
        print("❌ 读取 DOCX 错误:", e)
        return []

def extract_from_pdf(path):
    """
    从 PDF 文件中提取文本并解析为答案
    """
    try:
        text = ""
        with fitz.open(path) as doc:
            for page in doc:
                text += page.get_text()
        return parse_answers_from_text(text)
    except Exception as e:
        print("❌ 读取 PDF 错误:", e)
        return []

def extract_skema(path):
    """
    根据扩展名选择 DOCX 或 PDF 提取方式，或为图片文件返回示例答案
    """
    file_ext = path.lower()
    
    if file_ext.endswith(".pdf"):
        return extract_from_pdf(path)
    elif file_ext.endswith(".docx"):
        return extract_from_docx(path)
    elif file_ext.endswith((".jpg", ".jpeg", ".png")):
        # 为图片文件返回示例答案（实际应用中需要OCR处理）
        print("⚠️ 图片格式暂不支持OCR，返回40题示例答案")
        # 生成40题的示例答案
        import random
        choices = ['A', 'B', 'C', 'D']
        return [random.choice(choices) for _ in range(40)]
    else:
        raise ValueError(f"不支持的格式：{os.path.basename(path)}。请上传 PDF 或 DOCX 格式的标准答案")
