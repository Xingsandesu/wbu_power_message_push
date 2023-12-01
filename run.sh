#!/bin/bash

# 设置工作目录
target_directory=""

# 切换到目标目录
cd "$target_directory"

docker run -itd \
    --privileged \
    --network bridge \
    --rm \
    --name power \
    -p 8080:8080 \
    -v "$(pwd)"/config.yaml:/app/config.yaml \
    -v "$(pwd)"/.power.yaml:/app/.power.yaml \
    -v "$(pwd)"/adb_logs:/app/adb_logs \
    -v "$(pwd)"/main_logs:/app/main_logs \
    -v "$(pwd)"/proxy_logs:/app/proxy_logs \
    -v "$(pwd)"/keys:/root/.android \
    fushin/wbupowerapi
