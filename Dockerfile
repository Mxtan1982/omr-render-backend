# 使用 Python 官方镜像
FROM python:3.10-slim

# 安装 tesseract-ocr 和其他依赖
RUN apt-get update && \
    apt-get install -y tesseract-ocr libglib2.0-0 libsm6 libxext6 libxrender1 && \
    rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 把当前目录代码复制到容器
COPY . /app

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露端口（Render 会自动用 $PORT）
EXPOSE 8080

# 容器启动时执行
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "--timeout", "120", "main:app"]
