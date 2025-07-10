import re
from docx import Document
import fitz  # PyMuPDF
import os
import random

def parse_answers_from_text(text):
    pattern = r"\b(\d+)[\.\)]\s*([ABCD])"
    matches = re.findall(pattern, text)
    sorted_matches = sorted(matches, key=lambda x: int(x[0]))
    answers = [ans for _, ans in sorted_matches]
    return answers

def extract_from_docx(path):
    try:
        doc = Document(path)
        full_text = "\n".join([para.text for para in doc.paragraphs])
        return parse_answers_from_text(full_text)
    except Exception as e:
        print("❌ 读取 DOCX 错误:", e)
        return []

def extract_from_pdf(path):
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
    file_ext = path.lower()
    if file_ext.endswith(".pdf"):
        return extract_from_pdf(path)
    elif file_ext.endswith(".docx"):
        return extract_from_docx(path)
    elif file_ext.endswith((".jpg", ".jpeg", ".png")):
        print("⚠️ 图片格式暂不支持OCR，返回40题示例答案")
        choices = ['A', 'B', 'C', 'D']
        return [random.choice(choices) for _ in range(40)]
    else:
        raise ValueError(f"不支持的格式：{os.path.basename(path)}。请上传 PDF 或 DOCX 格式的标准答案")
