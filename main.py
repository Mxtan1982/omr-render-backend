import pytesseract
import cv2
import os
import re
import random

# ================================
# 🎯 学生名字识别
# ================================
def extract_student_name(image_path, template_name=None):
    """
    从答题卡图像用 OCR 识别学生名字区域
    如果识别不到，fallback 用文件名
    """
    text = ""

    try:
        # 读取图片
        img = cv2.imread(image_path)

        # ✅ 根据你的答题卡调整坐标！下面是示例值
        # 左上角大概放 `NAMA` 一行区域
        x, y, w, h = 30, 20, 500, 100  # 你可以根据实际答题卡微调

        # 截取名字区域
        name_region = img[y:y + h, x:x + w]

        # 灰度化
        gray = cv2.cvtColor(name_region, cv2.COLOR_BGR2GRAY)

        # 二值化（可选）
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 用 pytesseract OCR
        text = pytesseract.image_to_string(thresh, lang="eng").strip()

        if text:
            print(f"✅ OCR 识别到名字：{text}")

    except Exception as e:
        print(f"⚠️ OCR 出错：{e}")

    # 如果没识别到就用文件名推测
    if not text or len(text) < 2:
        text = fallback_name_from_filename(image_path)
        print(f"✅ 使用文件名推测：{text}")

    return text


# ================================
# 🎯 文件名 fallback 方法
# ================================
def fallback_name_from_filename(image_path):
    """
    如果 OCR 失败，就用文件名推测
    """
    filename = os.path.splitext(os.path.basename(image_path))[0]

    if "WhatsApp" in filename or "WA" in filename:
        time_match = re.search(r'(\d{2}\.\d{2}\.\d{2})', filename)
        if time_match:
            return f"学生_{time_match.group(1).replace('.', '')}"
        parts = filename.split('_')
        if len(parts) > 1:
            return f"学生_{parts[-1][:8]}"

    clean_name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '_', filename)
    clean_name = re.sub(r'_+', '_', clean_name).strip('_')

    return clean_name[:20] if clean_name else "Student_Unknown"


# ================================
# 🎯 学生答案（示例随机）
# ================================
def extract_student_answers(image_path, total_questions):
    """
    临时示例：随机生成学生答案
    以后可换成真正的 OMR 圈读识别
    """
    choices = ['A', 'B', 'C', 'D']
    print(f"📝 生成 {total_questions} 题学生答案")
    return [random.choice(choices) for _ in range(total_questions)]
