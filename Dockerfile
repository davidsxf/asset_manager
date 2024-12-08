# 使用Python官方镜像作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 安装系统依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 升级pip
RUN pip install --upgrade pip

# 复制项目依赖文件
COPY requirements.txt .

# 安装项目依赖
RUN pip install -r requirements.txt

# 创建数据目录
RUN mkdir /app/data

# 复制项目文件
COPY . .

# 创建static和media目录
RUN mkdir -p /app/static /app/media

# 设置权限
RUN chmod -R 755 /app 