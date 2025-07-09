import os
import re
import random

def extract_student_name(image_path):
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
    choices = ['A', 'B', 'C', 'D']
    print(f"📝 Generating {total_questions} answers", flush=True)
    return [random.choice(choices) for _ in range(total_questions)]
