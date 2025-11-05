#!/usr/bin/env python3
"""
安装 stable_fast 的辅助脚本
支持多种下载方式：直接下载、GitHub 镜像代理等
"""
import os
import sys
import subprocess
import urllib.request
import tempfile

STABLE_FAST_URL = "https://github.com/chengzeyi/stable-fast/releases/download/v0.0.15.post1/stable_fast-0.0.15.post1+torch211cu121-cp310-cp310-manylinux2014_x86_64.whl"

# GitHub 镜像代理列表（按优先级排序）
MIRRORS = [
    "https://ghproxy.com/",
    "https://github.com.cnpmjs.org/",
    "https://hub.fastgit.xyz/",
    "https://mirror.ghproxy.com/",
    "",  # 原始地址（最后尝试）
]


def download_with_mirror(url, mirror_prefix=""):
    """尝试使用镜像下载"""
    try:
        full_url = mirror_prefix + url if mirror_prefix else url
        print(f"尝试下载: {full_url}")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.whl') as tmp_file:
            urllib.request.urlretrieve(full_url, tmp_file.name)
            return tmp_file.name
    except Exception as e:
        print(f"下载失败: {e}")
        return None


def install_stable_fast():
    """安装 stable_fast"""
    print("正在安装 stable_fast...")
    
    # 方法1: 尝试使用镜像下载
    for mirror in MIRRORS:
        whl_path = download_with_mirror(STABLE_FAST_URL, mirror)
        if whl_path:
            try:
                print(f"使用本地文件安装: {whl_path}")
                subprocess.check_call([sys.executable, "-m", "pip", "install", whl_path])
                os.unlink(whl_path)
                print("✓ stable_fast 安装成功！")
                return True
            except Exception as e:
                print(f"安装失败: {e}")
                if os.path.exists(whl_path):
                    os.unlink(whl_path)
    
    # 方法2: 尝试直接使用 pip 安装（如果网络允许）
    print("\n尝试直接使用 pip 安装...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", STABLE_FAST_URL])
        print("✓ stable_fast 安装成功！")
        return True
    except Exception as e:
        print(f"直接安装失败: {e}")
    
    # 方法3: 提供手动安装说明
    print("\n" + "="*60)
    print("自动安装失败，请手动安装：")
    print("="*60)
    print(f"1. 手动下载文件: {STABLE_FAST_URL}")
    print("2. 或使用以下命令:")
    print(f"   wget {STABLE_FAST_URL} -O stable_fast.whl")
    print("   pip install stable_fast.whl")
    print("\n或者使用代理:")
    print(f"   pip install --proxy http://your-proxy:port {STABLE_FAST_URL}")
    print("="*60)
    return False


if __name__ == "__main__":
    success = install_stable_fast()
    sys.exit(0 if success else 1)

