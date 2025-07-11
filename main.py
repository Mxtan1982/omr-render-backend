import os
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import cv2
import pytesseract
import pandas as pd
import random

app = Flask(__name__)

# 基础配置
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class OMRProcessor:
    @staticmethod
    def process_image(filepath):
        """处理答题卡图片并返回结果"""
        try:
            # 1. 识别学生姓名
            img = cv2.imread(filepath)
            name = OMRProcessor._extract_name(img) if img is not None else "未知学生"
            
            # 2. 生成模拟答案 (实际项目应替换为真实识别逻辑)
            answers = [random.choice(['A', 'B', 'C', 'D']) for _ in range(20)]
            
            # 3. 保存结果
            result_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result.xlsx')
            pd.DataFrame({
                '学生姓名': [name],
                **{f'题{i+1}': [ans] for i, ans in enumerate(answers)}
            }).to_excel(result_path, index=False)
            
            return {'name': name, 'answers': answers, 'excel_path': result_path}
        except Exception as e:
            raise RuntimeError(f"处理失败: {str(e)}")

    @staticmethod
    def _extract_name(img):
        """从图片中识别学生姓名"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(gray, lang='chi_sim+eng')
        return text.strip() if text else "未识别到姓名"

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传答题卡图片"""
    if 'file' not in request.files:
        return jsonify({'error': '未上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '空文件名'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': '仅支持PNG/JPG/JPEG格式'}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        result = OMRProcessor.process_image(filepath)
        os.remove(filepath)  # 清理上传文件
        
        return jsonify({
            'status': 'success',
            'student_name': result['name'],
            'answers': result['answers']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download')
def download_result():
    """下载处理结果"""
    excel_path = os.path.join(app.config['UPLOAD_FOLDER'], 'result.xlsx')
    if not os.path.exists(excel_path):
        return jsonify({'error': '结果文件不存在，请先上传处理'}), 404
    
    return send_file(
        excel_path,
        as_attachment=True,
        download_name='omr_result.xlsx'
    )

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
