# 多阶段构建 - 后端服务
FROM python:3.11-slim

LABEL maintainer="Health Check System"
LABEL description="Backend API for Health Check Management System"

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖（使用清华镜像加速）
RUN pip install --no-cache-dir -r requirements.txt \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装生产环境需要的 WSGI 服务器
RUN pip install --no-cache-dir gunicorn \
    -i https://pypi.tuna.tsinghua.edu.cn/simple

# 复制应用代码
COPY . .

# 创建实例目录（用于存放数据库）
RUN mkdir -p instance

# 创建日志目录
RUN mkdir -p logs

# 暴露端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=run.py
ENV PYTHONUNBUFFERED=1

# 启动命令
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "run:app"]
