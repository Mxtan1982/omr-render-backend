import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import pytesseract
import pandas as pd
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
from docx import Document
import logging
import numpy as np
from io import BytesIO

# 初始化Flask应用
app = Flask(__name__)
CORS(app)

# 配置
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB限制
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'pdf', 'docx'}

# 创建上传目录
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OMRProcessor:
    def __init__(self):
        self.name_region = (30, 20, 500, 100)  # x,y,w,h

    def process_file(self, filepath: str, total_questions: int = 20):
        """处理上传文件的主方法"""
        try:
            # 1. 提取学生姓名
            student_name = self._extract_student_name(filepath)
            
            # 2. 识别答案 (示例用随机答案)
            answers = self._generate_sample_answers(total_questions)
            
            # 3. 生成Excel结果
            excel_path = self._save_to_excel(student_name, answers)
            
            return {
                "status": "success",
                "student_name": student_name,
                "answers": answers,
                "excel_path": excel_path
            }
        except Exception as e:
            logger.error(f"处理失败: {str(e)}")
            raise

    def _extract_student_name(self, filepath: str) -> str:
        """从文件中提取学生姓名"""
        try:
            # 根据文件类型选择处理方式
            if filepath.lower().endswith('.pdf'):
                img = self._pdf_to_image(filepath)
            elif filepath.lower().endswith('.docx'):
                img = self._docx_to_image(filepath)
            else:
                img = cv2.imread(filepath)
            
            if img is None:
                raise ValueError("无法读取文件内容")
            
            # 裁剪姓名区域
            x, y, w, h = self.name_region
            name_region = img[y:y+h, x:x+w]
            
            # 使用OpenCV预处理
            gray = cv2.cvtColor(name_region, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 使用Tesseract OCR
            text = pytesseract.image_to_string(thresh, lang='chi_sim+eng').strip()
            
            return text if text else self._get_name_from_filename(filepath)
            
        except Exception as e:
            logger.warning(f"姓名识别失败: {str(e)}")
            return self._get_name_from_filename(filepath)

    def _pdf_to_image(self, pdf_path: str) -> np.ndarray:
        """将PDF第一页转为OpenCV图像"""
        doc = fitz.open(pdf_path)
        page = doc.load_page(0)
        pix = page.get_pixmap()
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape((pix.h, pix.w, 3))
        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    def _docx_to_image(self, docx_path: str) -> np.ndarray:
        """将DOCX内容转为图像 (简化示例)"""
        doc = Document(docx_path)
        text = '\n'.join([para.text for para in doc.paragraphs][:3])
        img = np.zeros((300, 600, 3), dtype=np.uint8)
        img.fill(255)
        cv2.putText(img, text[:100], (30, 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0), 2)
        return img

    def _get_name_from_filename(self, filename: str) -> str:
        """从文件名提取学生姓名"""
        name = os.path.splitext(os.path.basename(filename))[0]
        clean_name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '_', name)
        return clean_name[:20] or "未知学生"

    def _generate_sample_answers(self, total: int) -> list:
        """生成示例答案 (实际项目应替换为真实识别逻辑)"""
        return [random.choice(['A', 'B', 'C', 'D']) for _ in range(total)]

    def _save_to_excel(self, name: str, answers: list) -> str:
        """保存结果到Excel"""
        data = {
            "学生姓名": [name],
            **{f"第{i+1}题": [ans] for i, ans in enumerate(answers)}
        }
        df = pd.DataFrame(data)
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'results.xlsx')
        df.to_excel(output_path, index=False)
        return output_path

# 初始化处理器
processor = OMRProcessor()

@app.route('/')
def home():
    return """
    <h1>OMR答题卡处理系统</h1>
    <p>API端点：</p>
    <ul>
        <li>POST /api/upload - 上传答题卡</li>
        <li>GET /api/download - 下载结果</li>
    </ul>
    """

@app.route('/health')
def health_check():
    """健康检查端点 (Render需要)"""
    return jsonify({"status": "healthy"}), 200

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """文件上传处理"""
    if 'file' not in request.files:
        return jsonify({"error": "未上传文件"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "空文件名"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "不支持的文件类型"}), 400
    
    try:
        # 保存上传文件
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        
        # 处理文件
        result = processor.process_file(save_path)
        
        # 清理上传文件 (保留结果文件)
        if os.path.exists(save_path) and not save_path.endswith('results.xlsx'):
            os.remove(save_path)
            
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"处理错误: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/download')
def download_results():
    """下载结果文件"""
    excel_path = os.path.join(app.config['UPLOAD_FOLDER'], 'results.xlsx')
    if not os.path.exists(excel_path):
        return jsonify({"error": "结果文件不存在"}), 404
        
    return send_file(
        excel_path,
        as_attachment=True,
        download_name='omr_results.xlsx'
    )

def allowed_file(filename):
    """检查文件扩展名是否合法"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# 启动配置
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
else:
    # 为Gunicorn提供应用实例
    gunicorn_app = app
