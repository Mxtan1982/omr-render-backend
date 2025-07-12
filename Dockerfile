# 基础镜像，用带有 tesseract 的官方 Debian
FROM python:3.10-slim

# 安装系统依赖：tesseract + opencv 所需的库
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr libgl1-mesa-glx libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 并安装
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 复制你的项目所有代码
COPY . .

# 可选：示范下载一个 tar.gz 并解压（可删除）
# RUN curl -fSL https://example.com/mydata.tar.gz -o data.tar.gz \
#     && tar -tzf data.tar.gz \
#     && tar -xzf data.tar.gz -C /app \
#     && rm data.tar.gz

# 默认用 gunicorn 启动 Flask app，绑定 0.0.0.0:8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--timeout", "120", "main:app"]
