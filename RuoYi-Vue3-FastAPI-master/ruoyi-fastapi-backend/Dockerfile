# 使用官方Python 3.12 slim镜像作为基础镜像
FROM python:3.12-slim

# 构建参数：指定构建环境（dev/prod），默认 prod
# 使用方式：docker build --build-arg BUILD_ENV=dev -t testapp:v1 .
ARG BUILD_ENV=prod

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    APP_ENV=${BUILD_ENV}

# 安装系统依赖（用于编译Python包的C扩展，如cryptography、numpy、pandas等）
# 注意：不需要MySQL客户端库，因为项目使用PyMySQL和asyncmy（纯Python实现）
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY . .

# 创建必要的目录
RUN mkdir -p vf_admin/upload_path \
    vf_admin/download_path \
    vf_admin/gen_path \
    vf_admin/task_test_data \
    logs

# 设置权限
RUN chmod -R 755 vf_admin logs

# 暴露端口（默认9099，可通过环境变量修改）
EXPOSE 9099

# 健康检查（检查应用是否在运行）
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.settimeout(1); result=s.connect_ex(('localhost', 9099)); s.close(); exit(0 if result == 0 else 1)" || exit 1

# 启动命令
# 注意：
# 1. APP_ENV 环境变量在构建时通过 BUILD_ENV 参数设置，默认 prod
# 2. 运行时需要挂载对应的 .env 文件：-v $(pwd)/.env.dev:/app/.env.dev
# 3. 可以通过 -e APP_ENV=dev 在运行时覆盖构建时的环境设置
CMD ["python", "app.py"]
