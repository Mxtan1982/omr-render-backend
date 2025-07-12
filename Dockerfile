# ✅ 使用官方 Python 镜像
FROM python:3.10-slim

# ✅ 安装 Tesseract OCR 和中文语言包
RUN apt-get update && \
    apt-get install -y tesseract-ocr tesseract-ocr-chi-sim libglib2.0-0 libsm6 libxext6 libxrender1 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# ✅ 设置工作目录
WORKDIR /app

# ✅ 复制文件
COPY requirements.txt ./
COPY main.py ./

# ✅ 安装依赖
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# ✅ 运行 gunicorn，绑定到 Render 的 $PORT
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--timeout", "120", "main:app"]
