#!/bin/bash
# 清理缓存脚本
# 用于释放数据盘空间

echo "=========================================="
echo "清理缓存脚本"
echo "=========================================="
echo ""

# 显示清理前空间
echo "清理前空间使用："
df -h /root/autodl-tmp | tail -1
echo ""

# 1. 清理 pip 缓存
echo "1. 清理 pip 缓存..."
PIP_CACHE_SIZE=$(du -sh /root/autodl-tmp/.cache/pip 2>/dev/null | cut -f1)
echo "   pip 缓存大小: $PIP_CACHE_SIZE"

if [ -d "/root/autodl-tmp/.cache/pip" ]; then
    # 尝试使用 pip cache purge（如果支持）
    pip cache purge 2>/dev/null || true
    
    # 直接删除缓存目录
    rm -rf /root/autodl-tmp/.cache/pip/*
    echo "   ✓ pip 缓存已清理"
else
    echo "   - pip 缓存目录不存在"
fi
echo ""

# 2. 清理临时文件（保留最近 3 天的）
echo "2. 清理临时文件（删除 3 天前的文件）..."
TMP_SIZE_BEFORE=$(du -sh /root/autodl-tmp/tmp 2>/dev/null | cut -f1 || echo "0")
echo "   临时文件大小: $TMP_SIZE_BEFORE"

if [ -d "/root/autodl-tmp/tmp" ]; then
    find /root/autodl-tmp/tmp -type f -mtime +3 -delete 2>/dev/null
    find /root/autodl-tmp/tmp -type d -empty -delete 2>/dev/null
    echo "   ✓ 临时文件已清理"
else
    echo "   - 临时文件目录不存在"
fi
echo ""

# 3. 清理 Python __pycache__
echo "3. 清理 Python __pycache__..."
find /root/StreamDiffusion -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find /root/StreamDiffusion -type f -name "*.pyc" -delete 2>/dev/null || true
echo "   ✓ Python 缓存已清理"
echo ""

# 4. 清理构建文件
echo "4. 清理构建文件..."
if [ -d "/root/StreamDiffusion/demo/realtime-comfyui-workflow/frontend/node_modules" ]; then
    # 不删除 node_modules，但可以清理 .svelte-kit
    rm -rf /root/StreamDiffusion/demo/realtime-comfyui-workflow/frontend/.svelte-kit 2>/dev/null || true
    echo "   ✓ 前端构建缓存已清理"
fi
echo ""

# 显示清理后空间
echo "=========================================="
echo "清理后空间使用："
df -h /root/autodl-tmp | tail -1
echo "=========================================="

# 显示各目录大小
echo ""
echo "各缓存目录大小："
echo "  pip 缓存:      $(du -sh /root/autodl-tmp/.cache/pip 2>/dev/null | cut -f1 || echo '0')"
echo "  HF 缓存:       $(du -sh /root/autodl-tmp/.cache/huggingface 2>/dev/null | cut -f1 || echo '0')"
echo "  临时文件:      $(du -sh /root/autodl-tmp/tmp 2>/dev/null | cut -f1 || echo '0')"
echo ""

