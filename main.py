import os
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import pandas as pd
from datetime import datetime
import cv2
import pytesseract
import random

from utils import fallback_name_from_filename

UPLOAD_FOLDER = "/tmp/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

results_cache = []

@app.route("/")
def index():
    return jsonify({"message": "✅ OMR Marker is running!"})

@app.route("/grade", methods=["POST"])
def grade():
    skema = request.files.get("skema")
    student = request.files.get("student")
    if not skema or not student:
        return jsonify({"error": "Missing skema or student file"}), 400

    skema_filename = secure_filename(skema.filename)
    student_filename = secure_filename(student.filename)
    skema_path = os.path.join(UPLOAD_FOLDER, skema_filename)
    student_path = os.path.join(UPLOAD_FOLDER, student_filename)
    skema.save(skema_path)
    student.save(student_path)

    # ✅ 假的 skema 解析（示例 40题）
    skema_answers = ['A'] * 40
    student_answers = ['A'] * 40

    # ✅ 简单模拟对比
    correct = [i+1 for i, (a,b) in enumerate(zip(skema_answers, student_answers)) if a == b]
    incorrect = [i+1 for i in range(len(skema_answers)) if i+1 not in correct]

    # ✅ OCR 识别学生名字
    img = cv2.imread(student_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, lang='eng+chi_sim').strip()
    student_name = text if len(text) >= 2 else fallback_name_from_filename(student_path)

    result = {
        "name": student_name,
        "score": len(correct),
        "total": len(skema_answers),
        "correct": correct,
        "incorrect": incorrect
    }
    results_cache.append(result)
    return jsonify(result)

@app.route("/export-excel")
def export_excel():
    if not results_cache:
        return jsonify({"error": "No results"}), 400

    df = pd.DataFrame(results_cache)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"/tmp/results_{now}.xlsx"
    df.to_excel(filepath, index=False)
    return send_file(filepath, as_attachment=True)
