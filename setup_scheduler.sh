#!/bin/bash

# Cloud Scheduler ジョブ作成スクリプト

PROJECT_ID="racing-ai-system-12345"
REGION="us-central1"
SERVICE_NAME="keiba-ai-bot"

# サービスアカウント作成（存在しない場合）
gcloud iam service-accounts create scheduler-sa \
    --display-name="Scheduler Service Account" \
    --project=$PROJECT_ID

# Cloud Run Invoker 権限付与
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:scheduler-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/run.invoker"

# Cloud Run サービスURL取得
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)' --project=$PROJECT_ID)

# 毎日午前10時に予想実行するスケジューラー作成
gcloud scheduler jobs create http daily-prediction \
    --schedule="0 10 * * *" \
    --uri="$SERVICE_URL/scheduled-prediction" \
    --http-method=POST \
    --oidc-service-account-email="scheduler-sa@$PROJECT_ID.iam.gserviceaccount.com" \
    --time-zone="Asia/Tokyo" \
    --description="Daily horse racing prediction at 10:00 AM JST" \
    --project=$PROJECT_ID \
    --location=$REGION

echo "Scheduler job created successfully!"
echo "Service URL: $SERVICE_URL"
echo "Next prediction will run at 10:00 AM JST daily"
