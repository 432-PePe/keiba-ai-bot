# 競馬予想AI LINE Bot Dockerfile
FROM python:3.11-slim

# 作業ディレクトリ設定
WORKDIR /app

# 依存関係コピー・インストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコピー
COPY . .

# ポート設定
EXPOSE 8080

# アプリケーション起動
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
