import os
import re
import random

def extract_student_name(image_path):
    """
    根据文件名自动生成学生名字。
    - 如果文件名里包含 WhatsApp，尝试提取时间戳或后缀；
    - 否则对文件名进行清理，只保留中英文和数字；
    - 如果结果为空就返回 'Student_Unknown'。
    """
    filename = os.path.splitext(os.path.basename(image_path))[0]

    if "WhatsApp" in filename:
        time_match = re.search(r'(\d{2}\.\d{2}\.\d{2})', filename)
        if time_match:
            time_str = time_match.group(1).replace('.', '')
            return f"学生_{time_str}"
        else:
            parts = filename.split('_')
            if len(parts) > 1:
                return f"学生_{parts[-1][:8]}"

    clean_name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '_', filename)
    clean_name = re.sub(r'_+', '_', clean_name).strip('_')
    return clean_name[:20] if clean_name else "Student_Unknown"


def extract_student_answers(image_path, total_questions):
    """
    临时代替 OMR 检测：随机生成 ABCD 选项，用于测试。
    实际可以接入 OpenCV 或 EasyOCR 做真实识别。
    """
    choices = ['A', 'B', 'C', 'D']
    print(f"📝 生成 {total_questions} 题的学生答案", flush=True)
    return [random.choice(choices) for _ in range(total_questions)]
