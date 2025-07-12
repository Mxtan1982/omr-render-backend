import os
from flask import Flask, request, jsonify
import cv2
import pytesseract

app = Flask(__name__)

UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return jsonify({"message": "✅ OMR OCR API Running"})

@app.route("/ocr", methods=["POST"])
def ocr():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty file name"}), 400

    # 保存上传文件
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # OpenCV 读取 + pytesseract OCR
    img = cv2.imread(filepath)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, lang="eng+chi_sim")
    result = text.strip() or "未识别到内容"

    # 返回结果
    return jsonify({
        "filename": file.filename,
        "recognized_text": result
    })

if __name__ == "__main__":
    # 本地调试可用，生产用 gunicorn
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
