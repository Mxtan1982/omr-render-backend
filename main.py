from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import os
import pandas as pd
from datetime import datetime
from werkzeug.utils import secure_filename

from utils import extract_student_name, extract_student_answers
from skema_parser import extract_skema

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

results_cache = []

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/grade", methods=["POST"])
def grade():
    skema_file = request.files.get("skema")
    student_file = request.files.get("student")

    if not skema_file or not student_file:
        return jsonify({"error": "Missing skema or student file"}), 400

    if not allowed_file(skema_file.filename) or not allowed_file(student_file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    skema_path = os.path.join(UPLOAD_FOLDER, secure_filename(skema_file.filename))
    student_path = os.path.join(UPLOAD_FOLDER, secure_filename(student_file.filename))
    skema_file.save(skema_path)
    student_file.save(student_path)

    skema_answers = extract_skema(skema_path)
    total_questions = len(skema_answers)
    if total_questions == 0:
        return jsonify({"error": "Skema extraction failed. Please check file format."}), 400

    student_answers = extract_student_answers(student_path, total_questions)
    correct = [i+1 for i, (a,b) in enumerate(zip(skema_answers, student_answers)) if a == b]
    incorrect = [i+1 for i in range(total_questions) if (i+1) not in correct]
    student_name = extract_student_name(student_path)

    result = {
        "name": student_name,
        "score": len(correct),
        "total": total_questions,
        "correct": correct,
        "incorrect": incorrect
    }

    results_cache.append(result)
    return jsonify(result)

@app.route("/export-excel")
def export_excel():
    if not results_cache:
        return jsonify({"error": "No results to export"}), 400

    df = pd.DataFrame(results_cache)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"/tmp/results_{now}.xlsx"
    df.to_excel(file_path, index=False)
    return send_file(file_path, as_attachment=True)
