# 基础 Python 镜像
FROM python:3.10-slim

# 安装 tesseract 和中文/英文语言包
RUN apt-get update && \
    apt-get install -y tesseract-ocr libtesseract-dev libleptonica-dev \
    tesseract-ocr-chi-sim tesseract-ocr-eng \
    libglib2.0-0 libsm6 libxext6 libxrender-dev && \
    rm -rf /var/lib/apt/lists/*

# 工作目录
WORKDIR /app

# 复制依赖和代码
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# 容器对外开放端口
EXPOSE 8080

# 启动命令（CMD）
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--timeout", "120", "main:app"]
