FROM python:3.11-slim

# システムパッケージの更新とインストール
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリ設定
WORKDIR /app

# 依存関係ファイルをコピー
COPY requirements.txt .

# Pythonパッケージのインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY app/ ./app/

# 環境変数設定
ENV PYTHONPATH=/app
ENV PORT=8080

# 非rootユーザーでの実行
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/ || exit 1

# アプリケーション起動
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app.main:app
