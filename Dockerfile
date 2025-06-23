# マルチステージビルド: ビルドステージ
FROM python:3.11-slim as builder

# ビルド時の環境変数
ENV PYTHONUNBUFFERED=1     PYTHONDONTWRITEBYTECODE=1     PIP_NO_CACHE_DIR=1     PIP_DISABLE_PIP_VERSION_CHECK=1

# システムパッケージの更新とビルド依存関係のインストール
RUN apt-get update && apt-get install -y --no-install-recommends     build-essential     gcc     g++     libc6-dev     libffi-dev     libssl-dev     python3-dev     pkg-config     && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリの設定
WORKDIR /app

# requirements.txt をコピーして依存関係をインストール
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# =============================================================================
# 本番ステージ: 軽量な本番用イメージ
FROM python:3.11-slim as production

# 本番環境変数
ENV PYTHONUNBUFFERED=1     PYTHONDONTWRITEBYTECODE=1     PATH="/root/.local/bin:$PATH"     DEBIAN_FRONTEND=noninteractive     DISPLAY=:99     CHROME_BIN=/usr/bin/google-chrome     CHROMEDRIVER_PATH=/usr/bin/chromedriver

# システムパッケージの更新と本番依存関係のインストール
RUN apt-get update && apt-get install -y --no-install-recommends     # 基本システムツール
    curl     wget     gnupg     ca-certificates     apt-transport-https     software-properties-common     # 日本語フォントサポート
    fonts-noto-cjk     fonts-noto-cjk-extra     fonts-liberation     fontconfig     # Chrome/Selenium依存関係
    libnss3     libgconf-2-4     libxss1     libappindicator1     libindicator7     libappindicator3-1     libgtk-3-0     libxshmfence1     libglu1-mesa     # X11仮想ディスプレイ
    xvfb     # ネットワークツール
    dnsutils     iputils-ping     # プロセス管理
    supervisor     # 日本語ロケール
    locales     && rm -rf /var/lib/apt/lists/*

# 日本語ロケールの設定
RUN sed -i '/ja_JP.UTF-8/s/^# //g' /etc/locale.gen &&     locale-gen &&     update-locale LANG=ja_JP.UTF-8

ENV LANG=ja_JP.UTF-8     LANGUAGE=ja_JP:ja     LC_ALL=ja_JP.UTF-8

# Google Chrome の公式リポジトリを追加
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - &&     echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list

# Google Chrome のインストール
RUN apt-get update && apt-get install -y --no-install-recommends     google-chrome-stable     && rm -rf /var/lib/apt/lists/*

# ChromeDriver のインストール（最新版を自動取得）
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1-3) &&     CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}") &&     wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" &&     unzip /tmp/chromedriver.zip -d /tmp/ &&     mv /tmp/chromedriver /usr/bin/chromedriver &&     chmod +x /usr/bin/chromedriver &&     rm /tmp/chromedriver.zip

# アプリケーション用ユーザーの作成（セキュリティ向上）
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /bin/bash appuser

# 作業ディレクトリの設定
WORKDIR /app

# ビルドステージからPythonパッケージをコピー
COPY --from=builder /root/.local /root/.local

# アプリケーションファイルをコピー
COPY --chown=appuser:appuser . .

# ログディレクトリの作成
RUN mkdir -p /app/logs /app/data /app/cache &&     chown -R appuser:appuser /app

# Supervisor設定ファイルの作成
RUN echo '[supervisord]' > /etc/supervisor/conf.d/supervisord.conf &&     echo 'nodaemon=true' >> /etc/supervisor/conf.d/supervisord.conf &&     echo 'user=root' >> /etc/supervisor/conf.d/supervisord.conf &&     echo '' >> /etc/supervisor/conf.d/supervisord.conf &&     echo '[program:xvfb]' >> /etc/supervisor/conf.d/supervisord.conf &&     echo 'command=/usr/bin/Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset' >> /etc/supervisor/conf.d/supervisord.conf &&     echo 'autostart=true' >> /etc/supervisor/conf.d/supervisord.conf &&     echo 'autorestart=true' >> /etc/supervisor/conf.d/supervisord.conf &&     echo 'priority=100' >> /etc/supervisor/conf.d/supervisord.conf &&     echo '' >> /etc/supervisor/conf.d/supervisord.conf &&     echo '[program:flask-app]' >> /etc/supervisor/conf.d/supervisord.conf &&     echo 'command=/usr/local/bin/gunicorn --bind 0.0.0.0:8080 --workers 2 --timeout 300 --keep-alive 2 --max-requests 1000 --max-requests-jitter 100 app:app' >> /etc/supervisor/conf.d/supervisord.conf &&     echo 'directory=/app' >> /etc/supervisor/conf.d/supervisord.conf &&     echo 'user=appuser' >> /etc/supervisor/conf.d/supervisord.conf &&     echo 'autostart=true' >> /etc/supervisor/conf.d/supervisord.conf &&     echo 'autorestart=true' >> /etc/supervisor/conf.d/supervisord.conf &&     echo 'priority=200' >> /etc/supervisor/conf.d/supervisord.conf &&     echo 'stdout_logfile=/app/logs/flask.log' >> /etc/supervisor/conf.d/supervisord.conf &&     echo 'stderr_logfile=/app/logs/flask_error.log' >> /etc/supervisor/conf.d/supervisord.conf

# Chrome用の設定ファイル作成
RUN echo '#!/bin/bash' > /usr/local/bin/chrome-headless &&     echo 'exec google-chrome --headless --no-sandbox --disable-dev-shm-usage --disable-gpu --remote-debugging-port=9222 --window-size=1920,1080 "$@"' >> /usr/local/bin/chrome-headless &&     chmod +x /usr/local/bin/chrome-headless

# フォントキャッシュの更新
RUN fc-cache -fv

# ヘルスチェック用スクリプト
RUN echo '#!/bin/bash' > /usr/local/bin/healthcheck &&     echo 'curl -f http://localhost:8080/ || exit 1' >> /usr/local/bin/healthcheck &&     chmod +x /usr/local/bin/healthcheck

# ポート公開
EXPOSE 8080

# ヘルスチェック設定
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3     CMD /usr/local/bin/healthcheck

# ボリューム設定（データ永続化）
VOLUME ["/app/logs", "/app/data", "/app/cache"]

# 起動スクリプトの作成
RUN echo '#!/bin/bash' > /usr/local/bin/start-app &&     echo 'set -e' >> /usr/local/bin/start-app &&     echo '' >> /usr/local/bin/start-app &&     echo '# Chrome/ChromeDriverのバージョン確認' >> /usr/local/bin/start-app &&     echo 'echo "Chrome version: $(google-chrome --version)"' >> /usr/local/bin/start-app &&     echo 'echo "ChromeDriver version: $(chromedriver --version)"' >> /usr/local/bin/start-app &&     echo '' >> /usr/local/bin/start-app &&     echo '# 必要なディレクトリの作成' >> /usr/local/bin/start-app &&     echo 'mkdir -p /app/logs /app/data /app/cache' >> /usr/local/bin/start-app &&     echo 'chown -R appuser:appuser /app/logs /app/data /app/cache' >> /usr/local/bin/start-app &&     echo '' >> /usr/local/bin/start-app &&     echo '# 環境変数の確認' >> /usr/local/bin/start-app &&     echo 'echo "Environment check:"' >> /usr/local/bin/start-app &&     echo 'echo "PORT: ${PORT:-8080}"' >> /usr/local/bin/start-app &&     echo 'echo "GOOGLE_APPLICATION_CREDENTIALS: ${GOOGLE_APPLICATION_CREDENTIALS:-Not set}"' >> /usr/local/bin/start-app &&     echo 'echo "LINE_CHANNEL_ACCESS_TOKEN: ${LINE_CHANNEL_ACCESS_TOKEN:+Set}"' >> /usr/local/bin/start-app &&     echo 'echo "LINE_CHANNEL_SECRET: ${LINE_CHANNEL_SECRET:+Set}"' >> /usr/local/bin/start-app &&     echo '' >> /usr/local/bin/start-app &&     echo '# Supervisorでサービス起動' >> /usr/local/bin/start-app &&     echo 'exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf' >> /usr/local/bin/start-app &&     chmod +x /usr/local/bin/start-app

# 最終的な権限設定
RUN chown -R appuser:appuser /app

# デフォルトコマンド
CMD ["/usr/local/bin/start-app"]

# ビルド情報をラベルとして追加
LABEL maintainer="AI Racing Prediction System"       version="1.0.0"       description="Flask web application with LINE Bot integration for AI horse racing predictions"       chrome.version="stable"       python.version="3.11"       build.date="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"

# セキュリティ設定
USER appuser

# 環境変数のデフォルト値
ENV PORT=8080     FLASK_ENV=production     FLASK_APP=app.py     WORKERS=2     TIMEOUT=300     MAX_REQUESTS=1000
