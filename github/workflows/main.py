# 競馬予想AI LINE Bot メインアプリケーション
# Step 2-4で詳細実装予定

from fastapi import FastAPI

app = FastAPI(title="競馬予想AI LINE Bot")

@app.get("/")
async def root():
    return {"message": "競馬予想AI LINE Bot v12.2 - システム準備中"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# TODO: Step 2で LINE Webhook実装
# TODO: Step 3で 予想API実装
# TODO: Step 4で システム統合
