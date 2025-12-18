# tests/conftest.py
"""
Pytest 配置文件
"""
import pytest
import sys
import os

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 将 src 添加到 sys.path 的最前面
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 同时添加 src 目录本身
src_path = os.path.join(project_root, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

print(f"[conftest] 项目根目录: {project_root}")
print(f"[conftest] Python 路径: {sys.path[: 3]}")