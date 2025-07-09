import re
from docx import Document
import fitz  # PyMuPDF
import os
import random

def parse_answers_from_text(text):
    """
    从提取的纯文本中解析标准答案
    支持格式： 1. A  或  2) B  等
    返回： ['A', 'B', ...]
    """
    pattern = r"\b(\d+)[\.\)]\s*([ABCD])"
    matches = re.findall(pattern, text, flags=re.IGNORECASE)

    if not matches:
        print("⚠️ 未匹配到任何标准答案格式，请检查文本格式！")
        return []

    # 按题号升序排列
    sorted_matches = sorted(matches, key=lambda x: int(x[0]))
    answers = [ans.upper() for _, ans in sorted_matches]
    print(f"✅ 已解析到 {len(answers)} 题标准答案")
    return answers

def extract_from_docx(path):
    """
    从 Word DOCX 文件提取所有段落文本，然后解析答案
    """
    try:
        doc = Document(path)
        full_text = "\n".join(para.text for para in doc.paragraphs if para.text.strip())
        print(f"📄 DOCX 内容长度：{len(full_text)} 字符")
        return parse_answers_from_text(full_text)
    except Exception as e:
        print(f"❌ 读取 DOCX 出错: {e}")
        return []

def extract_from_pdf(path):
    """
    从 PDF 文件提取每页文本，然后解析答案
    """
    try:
        text = ""
        with fitz.open(path) as doc:
            for page in doc:
                page_text = page.get_text()
                text += page_text + "\n"
        print(f"📄 PDF 内容长度：{len(text)} 字符")
        return parse_answers_from_text(text)
    except Exception as e:
        print(f"❌ 读取 PDF 出错: {e}")
        return []

def extract_skema(path):
    """
    根据文件类型选择解析方式：
    - PDF: 调用 extract_from_pdf
    - DOCX: 调用 extract_from_docx
    - 图片: 返回示例随机答案
    """
    ext = os.path.splitext(path)[1].lower()

    if ext == ".pdf":
        print(f"🗂️ 解析 PDF: {path}")
        return extract_from_pdf(path)
    elif ext == ".docx":
        print(f"🗂️ 解析 DOCX: {path}")
        return extract_from_docx(path)
    elif ext in (".jpg", ".jpeg", ".png"):
        print(f"⚠️ 当前图片暂不支持 OCR，自动返回示例 40 题答案")
        return [random.choice(['A', 'B', 'C', 'D']) for _ in range(40)]
    else:
        raise ValueError(f"❌ 不支持的文件格式: {ext}，请上传 PDF 或 DOCX")
