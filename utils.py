import os
import re
import random

def extract_student_name(image_path):
    """
    从文件名提取学生名字，自动适配 WhatsApp/WA/IMG 格式，
    没有匹配时使用干净的文件名，保留中文、英文、数字。
    """
    filename = os.path.splitext(os.path.basename(image_path))[0]

    # ✅ 统一大写，方便匹配 WA/IMG
    name_upper = filename.upper()

    # WhatsApp 或 WA 格式示例：IMG-20230707-WA0001.jpg 或 WhatsApp Image ...
    if "WHATSAPP" in name_upper or "WA" in name_upper or "IMG" in name_upper:
        # 优先匹配时间戳格式（若有）
        time_match = re.search(r'(\d{2}\.\d{2}\.\d{2})', filename)
        if time_match:
            time_str = time_match.group(1).replace('.', '')
            return f"学生_{time_str}"

        # 尝试匹配数字 ID，如 WA0001 或 IMG20230707
        id_match = re.search(r'WA(\d+)', name_upper)
        if id_match:
            return f"学生_{id_match.group(1)}"
        
        # 最后用下划线分隔，取最后一段
        parts = filename.split('_')
        if len(parts) > 1:
            return f"学生_{parts[-1][:8]}"

    # 普通文件名：只保留中文、英文、数字，其他转为 _
    clean_name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '_', filename)
    clean_name = re.sub(r'_+', '_', clean_name).strip('_')

    # 如果仍然空，返回默认
    return clean_name[:20] if clean_name else "Student_Unknown"


def extract_student_answers(image_path, total_questions):
    """
    临时占位符，模拟学生答案，后期换成 OCR/OMR 逻辑
    """
    choices = ['A', 'B', 'C', 'D']
    print(f"📝 生成 {total_questions} 题答案", flush=True)
    return [random.choice(choices) for _ in range(total_questions)]
