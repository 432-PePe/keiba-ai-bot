import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    FlexSendMessage, BubbleContainer, BoxComponent,
    TextComponent, ButtonComponent, URIAction
)
import asyncio
from threading import Thread
import schedule
import time

# 内部モジュールのインポート
from src.race_analyzer import RaceAnalyzer
from src.prediction_engine import PredictionEngine
from src.data_collector import DataCollector
from src.scheduler import RaceScheduler
from config.settings import Config

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask アプリケーション初期化
app = Flask(__name__)
app.config.from_object(Config)

# LINE Bot API 初期化
line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))

# AI予想エンジン初期化
race_analyzer = RaceAnalyzer()
prediction_engine = PredictionEngine()
data_collector = DataCollector()
race_scheduler = RaceScheduler()

class KeibaBotApp:
    """競馬AI予想システムのメインアプリケーションクラス"""

    def __init__(self):
        self.daily_investment = 0
        self.max_daily_investment = 20000  # 1日の投資上限
        self.prediction_cache = {}
        self.race_results = []

    def reset_daily_stats(self):
        """日次統計のリセット"""
        self.daily_investment = 0
        self.prediction_cache = {}
        logger.info("Daily stats reset completed")

    async def generate_race_predictions(self, race_date=None):
        """レース予想の生成"""
        try:
            if not race_date:
                race_date = datetime.now().strftime('%Y-%m-%d')

            # キャッシュチェック
            cache_key = f"predictions_{race_date}"
            if cache_key in self.prediction_cache:
                return self.prediction_cache[cache_key]

            # レースデータ収集
            logger.info(f"Collecting race data for {race_date}")
            race_data = await data_collector.collect_race_data(race_date)

            if not race_data:
                return {"error": "No race data available for the specified date"}

            # レース分析
            logger.info("Analyzing race data")
            analyzed_races = []
            for race in race_data:
                analysis = await race_analyzer.analyze_race(race)
                if analysis:
                    analyzed_races.append(analysis)

            # AI予想生成
            logger.info("Generating AI predictions")
            predictions = []
            total_investment = 0

            for race_analysis in analyzed_races:
                if total_investment >= self.max_daily_investment:
                    break

                prediction = await prediction_engine.generate_prediction(race_analysis)
                if prediction and prediction.get('confidence', 0) > 0.7:
                    investment_amount = min(
                        prediction.get('recommended_bet', 1000),
                        self.max_daily_investment - total_investment
                    )

                    if investment_amount > 0:
                        prediction['investment_amount'] = investment_amount
                        predictions.append(prediction)
                        total_investment += investment_amount

            # 結果をキャッシュ
            result = {
                'date': race_date,
                'predictions': predictions,
                'total_investment': total_investment,
                'generated_at': datetime.now().isoformat()
            }

            self.prediction_cache[cache_key] = result
            self.daily_investment = total_investment

            logger.info(f"Generated {len(predictions)} predictions with total investment: ¥{total_investment}")
            return result

        except Exception as e:
            logger.error(f"Error generating predictions: {str(e)}")
            return {"error": f"Prediction generation failed: {str(e)}"}

    def format_predictions_message(self, predictions_data):
        """予想結果のLINEメッセージ形式化"""
        if 'error' in predictions_data:
            return TextSendMessage(text=f"❌ エラー: {predictions_data['error']}")

        predictions = predictions_data.get('predictions', [])
        if not predictions:
            return TextSendMessage(text="📊 本日は推奨レースがありません")

        # Flexメッセージの作成
        bubbles = []
        for i, pred in enumerate(predictions[:10]):  # 最大10レース
            bubble = BubbleContainer(
                body=BoxComponent(
                    layout="vertical",
                    contents=[
                        TextComponent(
                            text=f"🏇 {pred.get('race_name', 'レース情報')}",
                            weight="bold",
                            size="lg"
                        ),
                        TextComponent(
                            text=f"📍 {pred.get('track', '競馬場')} {pred.get('race_number', 'R')}R",
                            size="sm",
                            color="#666666"
                        ),
                        TextComponent(
                            text=f"⏰ {pred.get('race_time', '時刻未定')}",
                            size="sm",
                            color="#666666"
                        ),
                        TextComponent(
                            text=f"🎯 本命: {pred.get('top_pick', '未定')}",
                            weight="bold",
                            color="#FF5551"
                        ),
                        TextComponent(
                            text=f"📈 信頼度: {pred.get('confidence', 0):.1%}",
                            size="sm"
                        ),
                        TextComponent(
                            text=f"💰 推奨投資: ¥{pred.get('investment_amount', 0):,}",
                            weight="bold",
                            color="#0066CC"
                        ),
                        TextComponent(
                            text=f"📊 予想: {pred.get('prediction_type', '単勝')}",
                            size="sm"
                        )
                    ]
                )
            )
            bubbles.append(bubble)

        # 総投資額の追加
        summary_bubble = BubbleContainer(
            body=BoxComponent(
                layout="vertical",
                contents=[
                    TextComponent(
                        text="📋 本日の投資サマリー",
                        weight="bold",
                        size="lg"
                    ),
                    TextComponent(
                        text=f"💰 総投資額: ¥{predictions_data.get('total_investment', 0):,}",
                        weight="bold",
                        color="#0066CC"
                    ),
                    TextComponent(
                        text=f"🎯 推奨レース数: {len(predictions)}",
                        size="sm"
                    ),
                    TextComponent(
                        text=f"📅 {predictions_data.get('date', datetime.now().strftime('%Y-%m-%d'))}",
                        size="sm",
                        color="#666666"
                    )
                ]
            )
        )
        bubbles.append(summary_bubble)

        return FlexSendMessage(
            alt_text="🏇 本日の競馬AI予想",
            contents={
                "type": "carousel",
                "contents": [bubble.as_json_dict() for bubble in bubbles]
            }
        )

# アプリケーションインスタンス
keiba_bot = KeibaBotApp()

@app.route("/", methods=['GET'])
def health_check():
    """ヘルスチェックエンドポイント"""
    return jsonify({
        "status": "healthy",
        "service": "Keiba AI Bot",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route("/webhook", methods=['POST'])
def callback():
    """LINE Webhook エンドポイント"""
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature")
        abort(400)
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        abort(500)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """LINEメッセージハンドラー"""
    user_message = event.message.text.lower()
    user_id = event.source.user_id

    logger.info(f"Received message from {user_id}: {user_message}")

    try:
        if user_message in ['予想', '今日の予想', 'prediction']:
            # 今日の予想を生成
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            predictions = loop.run_until_complete(
                keiba_bot.generate_race_predictions()
            )
            loop.close()

            reply_message = keiba_bot.format_predictions_message(predictions)

        elif user_message in ['明日の予想', 'tomorrow']:
            # 明日の予想を生成
            tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            predictions = loop.run_until_complete(
                keiba_bot.generate_race_predictions(tomorrow)
            )
            loop.close()

            reply_message = keiba_bot.format_predictions_message(predictions)

        elif user_message in ['ヘルプ', 'help']:
            reply_message = TextSendMessage(
                text="""🏇 競馬AI予想Bot コマンド一覧

📊 「予想」「今日の予想」
→ 本日のAI予想を表示

📅 「明日の予想」
→ 明日のAI予想を表示

📈 「統計」
→ 予想成績を表示

❓ 「ヘルプ」
→ このメッセージを表示

🤖 毎日10時に自動で予想を配信します
💰 1日の投資上限: ¥20,000"""
            )

        elif user_message in ['統計', 'stats']:
            stats_text = f"""📈 予想統計情報

💰 本日の投資額: ¥{keiba_bot.daily_investment:,}
📊 残り投資可能額: ¥{keiba_bot.max_daily_investment - keiba_bot.daily_investment:,}
🎯 キャッシュ済み予想: {len(keiba_bot.prediction_cache)}件

📅 最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}"""

            reply_message = TextSendMessage(text=stats_text)

        else:
            reply_message = TextSendMessage(
                text="🤔 申し訳ございません。コマンドが認識できませんでした。\n「ヘルプ」と入力してコマンド一覧をご確認ください。"
            )

        line_bot_api.reply_message(event.reply_token, reply_message)

    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        error_message = TextSendMessage(
            text="❌ システムエラーが発生しました。しばらく時間をおいてから再度お試しください。"
        )
        line_bot_api.reply_message(event.reply_token, error_message)

@app.route("/manual-prediction", methods=['POST'])
def manual_prediction():
    """手動予想生成エンドポイント"""
    try:
        data = request.get_json()
        race_date = data.get('date', datetime.now().strftime('%Y-%m-%d'))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        predictions = loop.run_until_complete(
            keiba_bot.generate_race_predictions(race_date)
        )
        loop.close()

        return jsonify(predictions)

    except Exception as e:
        logger.error(f"Manual prediction error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/broadcast", methods=['POST'])
def broadcast_predictions():
    """予想の一斉配信エンドポイント"""
    try:
        # 今日の予想を生成
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        predictions = loop.run_until_complete(
            keiba_bot.generate_race_predictions()
        )
        loop.close()

        if 'error' not in predictions and predictions.get('predictions'):
            message = keiba_bot.format_predictions_message(predictions)

            # 全ユーザーに配信（実際の実装では登録ユーザーリストを使用）
            # line_bot_api.broadcast(message)

            logger.info("Broadcast completed successfully")
            return jsonify({"status": "success", "message": "Predictions broadcasted"})
        else:
            return jsonify({"status": "no_predictions", "message": "No predictions to broadcast"})

    except Exception as e:
        logger.error(f"Broadcast error: {str(e)}")
        return jsonify({"error": str(e)}), 500

def run_scheduler():
    """スケジューラーの実行"""
    # 毎日10時に予想配信
    schedule.every().day.at("10:00").do(lambda: requests.post(
        f"{os.environ.get('APP_URL', 'http://localhost:8080')}/broadcast"
    ))

    # 毎日0時に統計リセット
    schedule.every().day.at("00:00").do(keiba_bot.reset_daily_stats)

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # スケジューラーをバックグラウンドで実行
    scheduler_thread = Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    # Flaskアプリケーション起動
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
