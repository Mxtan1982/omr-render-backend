from flask import Flask, request, jsonify, send_file
import os
import cv2
import pytesseract
import re
import random
from werkzeug.utils import secure_filename
from typing import List, Optional, Tuple
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化Flask应用
app = Flask(__name__)

# 配置
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class OMRProcessor:
    def __init__(self):
        """初始化OMR处理器"""
        self.config = {
            'name_region': (30, 20, 500, 100),  # 名字区域坐标 (x,y,w,h)
            'default_lang': 'eng',
            'min_name_length': 2
        }

    def extract_student_name(self, image_path: str) -> str:
        """从图片中提取学生姓名"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("无法读取图片文件")
            
            x, y, w, h = self.config['name_region']
            name_region = img[y:y+h, x:x+w]
            
            # 图像预处理
            gray = cv2.cvtColor(name_region, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # OCR识别
            text = pytesseract.image_to_string(thresh, lang=self.config['default_lang']).strip()
            
            if text and len(text) >= self.config['min_name_length']:
                logger.info(f"识别到学生姓名: {text}")
                return text
                
        except Exception as e:
            logger.error(f"姓名识别错误: {str(e)}")
        
        # 使用文件名作为备选
        return self._fallback_name_from_filename(image_path)

    def _fallback_name_from_filename(self, image_path: str) -> str:
        """从文件名获取学生姓名"""
        filename = os.path.splitext(os.path.basename(image_path))[0]
        
        # 处理常见文件名模式
        if "WhatsApp" in filename or "WA" in filename:
            time_match = re.search(r'(\d{2}\.\d{2}\.\d{2})', filename)
            if time_match:
                return f"学生_{time_match.group(1).replace('.', '')}"
            
        # 清理文件名
        clean_name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '_', filename)
        clean_name = re.sub(r'_+', '_', clean_name).strip('_')
        return clean_name[:20] if clean_name else "未知学生"

    def extract_student_answers(self, image_path: str, total_questions: int) -> List[str]:
        """从图片中识别答案 (示例用随机答案)"""
        # TODO: 替换为实际的OMR识别逻辑
        choices = ['A', 'B', 'C', 'D']
        return [random.choice(choices) for _ in range(total_questions)]

# 初始化处理器
processor = OMRProcessor()

def allowed_file(filename):
    """检查文件扩展名是否合法"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """首页"""
    return """
    <h1>OMR答题卡识别系统</h1>
    <p>使用说明：</p>
    <ol>
        <li>POST /api/process 上传答题卡图片</li>
        <li>参数: file=图片文件, questions=题目数量(可选)</li>
    </ol>
    """

@app.route('/api/process', methods=['POST'])
def process_omr():
    """处理上传的OMR答题卡"""
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "未上传文件"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "未选择文件"}), 400
        
    if not allowed_file(file.filename):
        return jsonify({"status": "error", "message": "不支持的文件类型"}), 400
    
    # 获取题目数量 (默认为20)
    total_questions = request.form.get('questions', default=20, type=int)
    
    try:
        # 保存上传的文件
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 处理OMR答题卡
        student_name = processor.extract_student_name(filepath)
        answers = processor.extract_student_answers(filepath, total_questions)
        
        return jsonify({
            "status": "success",
            "student_name": student_name,
            "answers": answers,
            "total_questions": total_questions
        })
        
    except Exception as e:
        logger.error(f"处理失败: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"处理失败: {str(e)}"
        }), 500
        
    finally:
        # 清理上传的文件
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)

if __name__ == '__main__':
    # 从环境变量获取端口，默认10000
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
