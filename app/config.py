import os
from typing import Optional

class Config:
    """アプリケーション設定"""
    
    # LINE Bot設定
    LINE_CHANNEL_ACCESS_TOKEN: str = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '')
    LINE_CHANNEL_SECRET: str = os.environ.get('LINE_CHANNEL_SECRET', '')
    
    # Google Cloud設定
    GCP_PROJECT_ID: str = os.environ.get('GCP_PROJECT_ID', 'racing-ai-system-12345')
    
    # データベース設定（将来的にCloud SQLを使用する場合）
    DATABASE_URL: Optional[str] = os.environ.get('DATABASE_URL')
    
    # Redis設定（キャッシュ用）
    REDIS_URL: Optional[str] = os.environ.get('REDIS_URL')
    
    # AI分析設定
    MAX_ANALYSIS_TIME: int = 225  # 秒
    DAILY_INVESTMENT_LIMIT: int = 20000  # 円
    
    # データ収集設定
    JRA_BASE_URL: str = "https://www.jra.go.jp/JRADB/accessD.html"
    NETKEIBA_BASE_URL: str = "https://netkeiba.com/"
    KEIBALAB_BASE_URL: str = "https://keibalab.jp/"
    UMANITY_BASE_URL: str = "https://umanity.jp/"
    UMA_X_BASE_URL: str = "https://uma-x.jp/"
    MURYOU_KEIBA_AI_BASE_URL: str = "https://muryou-keiba-ai.jp/"
    
    # 品質基準
    REQUIRED_DATA_RATE: float = 1.0  # 100%
    RECOMMENDED_DATA_RATE: float = 0.95  # 95%
    
    # 文字化け対策
    ENCODING_PRIORITY: list = ['utf-8', 'shift_jis', 'euc-jp']
    
    # ログ設定
    LOG_LEVEL: str = os.environ.get('LOG_LEVEL', 'INFO')
    
    # 予想配信設定
    PREDICTION_SCHEDULE: str = "0 10 * * *"  # 毎日10時
    
    @classmethod
    def validate(cls):
        """設定の検証"""
        errors = []
        
        if not cls.LINE_CHANNEL_ACCESS_TOKEN:
            errors.append("LINE_CHANNEL_ACCESS_TOKEN is required")
        
        if not cls.LINE_CHANNEL_SECRET:
            errors.append("LINE_CHANNEL_SECRET is required")
        
        if not cls.GCP_PROJECT_ID:
            errors.append("GCP_PROJECT_ID is required")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")
        
        return True
