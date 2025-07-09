import os
import re
import random

def extract_student_name(image_path):
    """
    Extract student name from image file path or use a default naming scheme
    """
    # Extract filename without extension
    filename = os.path.splitext(os.path.basename(image_path))[0]

    # Clean up WhatsApp image names and generate meaningful student names
    if "WhatsApp" in filename:
        # Extract timestamp or use a counter for WhatsApp images
        import re
        # Try to extract time pattern like "08.01.01"
        time_match = re.search(r'(\d{2}\.\d{2}\.\d{2})', filename)
        if time_match:
            time_str = time_match.group(1).replace('.', '')
            return f"学生_{time_str}"
        else:
            # Use last part of filename as identifier
            parts = filename.split('_')
            if len(parts) > 1:
                return f"学生_{parts[-1][:8]}"

    # Extra cleanup for other filenames
    clean_name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '_', filename)
    clean_name = re.sub(r'_+', '_', clean_name).strip('_')

    if clean_name and len(clean_name) > 0:
        return clean_name[:20]
    else:
        return "Student_Unknown"

def extract_student_answers(image_path, total_questions):
    """
    Extract student answers from answer sheet image
    This is a placeholder implementation - in a real OMR system,
    you would use computer vision to detect filled bubbles
    """
    # Placeholder: return random answers for demonstration
    # In a real implementation, this would use image processing to detect filled circles
    choices = ['A', 'B', 'C', 'D']

    # Generate random answers for demonstration matching the total questions from skema
    # Replace this with actual OMR detection logic
    print(f"📝 生成 {total_questions} 题的学生答案")
    answers = []
    for i in range(total_questions):
        answers.append(random.choice(choices))

    return answers