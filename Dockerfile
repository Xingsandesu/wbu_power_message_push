FROM python:3.10.13-slim-bullseye
LABEL authors="huxin"

# 安装依赖
RUN apt-get update && \
    apt-get install -y android-tools-adb

# 设置环境变量
ENV PATH="${PATH}:/path/to/adb"

# 设置工作目录
WORKDIR /app

# 复制应用
COPY . /app

# 安装依赖

RUN pip install -r requirements.txt


# 入口命令
CMD ["python", "main.py"]
