from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import pandas as pd
from datetime import datetime
from werkzeug.utils import secure_filename

# 🟢 自己的工具模块（你之前写好的）
from utils import extract_student_name, extract_student_answers
from skema_parser import extract_skema

app = Flask(__name__)
CORS(app)

# 🟢 上传路径（Render 容器推荐 /tmp）
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🟢 内存缓存：记录所有批改结果
results_cache = []

# 🟢 允许上传的文件扩展名
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    """检查文件扩展名"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return jsonify({"message": "✅ OMR Marker is running! Use POST /grade to grade papers."})

@app.route("/grade", methods=["POST"])
def grade():
    skema_file = request.files.get("skema")
    student_file = request.files.get("student")
    # 🟢 前端/测试可传 student_name（可选）
    student_name = request.form.get("student_name")

    if not skema_file or not student_file:
        return jsonify({"error": "Missing skema or student file"}), 400

    if not allowed_file(skema_file.filename) or not allowed_file(student_file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    # 🟢 临时保存上传文件
    skema_path = os.path.join(UPLOAD_FOLDER, secure_filename(skema_file.filename))
    student_path = os.path.join(UPLOAD_FOLDER, secure_filename(student_file.filename))
    skema_file.save(skema_path)
    student_file.save(student_path)

    # 🟢 提取标准答案
    skema_answers = extract_skema(skema_path)
    total_questions = len(skema_answers)
    if total_questions == 0:
        return jsonify({"error": "Skema extraction failed, please check file format"}), 400

    # 🟢 生成学生答案（占位符随机）
    student_answers = extract_student_answers(student_path, total_questions)

    # 🟢 统计对错
    correct = [i+1 for i, (a,b) in enumerate(zip(skema_answers, student_answers)) if a == b]
    incorrect = [i+1 for i in range(total_questions) if i+1 not in correct]

    # 🟢 没传 student_name 时用自动识别
    if not student_name:
        student_name = extract_student_name(student_path)

    result = {
        "name": student_name,
        "score": len(correct),
        "total": total_questions,
        "correct": correct,
        "incorrect": incorrect
    }

    # 🟢 加入缓存
    results_cache.append(result)
    return jsonify(result)

@app.route("/export-excel", methods=["GET"])
def export_excel():
    if not results_cache:
        return jsonify({"error": "No results to export"}), 400

    df = pd.DataFrame(results_cache)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"/tmp/results_{now}.xlsx"
    df.to_excel(file_path, index=False)
    return send_file(file_path, as_attachment=True)

# 🟢 Render 部署不需要 app.run()
# if __name__ == "__main__":
#     app.run(debug=True)
