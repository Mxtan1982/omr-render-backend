import os
import re
import random

def extract_student_name(image_path):
    """
    从文件名提取学生名字，支持 WhatsApp 图片命名规则，也支持普通文件名。
    """
    filename = os.path.splitext(os.path.basename(image_path))[0]

    # WhatsApp 图片格式示例：IMG-20230707-WA0001.jpg
    if "WhatsApp" in filename or "WA" in filename:
        time_match = re.search(r'(\d{2}\.\d{2}\.\d{2})', filename)
        if time_match:
            time_str = time_match.group(1).replace('.', '')
            return f"学生_{time_str}"
        else:
            parts = filename.split('_')
            if len(parts) > 1:
                return f"学生_{parts[-1][:8]}"

    # 普通文件名：只保留中文英文数字
    clean_name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '_', filename)
    clean_name = re.sub(r'_+', '_', clean_name).strip('_')
    return clean_name[:20] if clean_name else "Student_Unknown"

def extract_student_answers(image_path, total_questions):
    """
    临时占位符，模拟学生答案，后期换成 OCR/OMR 逻辑
    """
    choices = ['A', 'B', 'C', 'D']
    print(f"📝 生成 {total_questions} 题答案", flush=True)
    return [random.choice(choices) for _ in range(total_questions)]
