# 基础镜像：官方 Python + Tesseract OCR
FROM python:3.10-slim

# 安装必要的系统依赖（包含 Tesseract）
RUN apt-get update && \
    apt-get install -y tesseract-ocr libgl1 && \
    rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . /app

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 启动命令：使用 gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]
