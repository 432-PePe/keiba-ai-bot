"""
AI競馬予想システム v3.1
競馬予想AI統合システム【プロモード専用最適化完全版】

このパッケージには以下のモジュールが含まれています：
- main.py: Flask Webアプリケーション
- config.py: 設定管理
- modules/: AI分析モジュール群
"""

__version__ = "3.1.0"
__author__ = "AI Horse Racing Prediction System"
__description__ = "競馬予想AI統合システム v3.1"

# パッケージ初期化
import os
import logging

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info(f"AI競馬予想システム v{__version__} が初期化されました")
