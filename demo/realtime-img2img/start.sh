#!/bin/bash
# 使用数据盘存储 pip 缓存和临时文件，避免占用系统盘
export PIP_CACHE_DIR=/root/autodl-tmp/.cache/pip
export TMPDIR=/root/autodl-tmp/tmp
export TMP=/root/autodl-tmp/tmp
export TEMP=/root/autodl-tmp/tmp

# 设置 Hugging Face 模型缓存目录到数据盘
export HF_HOME=/root/autodl-tmp/.cache/huggingface
export HUGGINGFACE_HUB_CACHE=/root/autodl-tmp/.cache/huggingface

cd frontend
npm install
npm run build
if [ $? -eq 0 ]; then
    echo -e "\033[1;32m\nfrontend build success \033[0m"
else
    echo -e "\033[1;31m\nfrontend build failed\n\033[0m" >&2  exit 1
fi
cd ../
python3 main.py --port 6006 --host 0.0.0.0 
