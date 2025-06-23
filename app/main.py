import os
import logging
from flask import Flask, request, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from datetime import datetime
import json

from .config import Config
from .modules.main_controller import MainController

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# LINE Bot API設定
line_bot_api = LineBotApi(Config.LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(Config.LINE_CHANNEL_SECRET)

# AI競馬予想コントローラー
ai_controller = MainController()

@app.route('/')
def health_check():
    """ヘルスチェック"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '3.1.0'
    })

@app.route('/webhook', methods=['POST'])
def callback():
    """LINE Webhook エンドポイント"""
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    app.logger.info(f"Request body: {body}")
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.error("Invalid signature. Please check your channel access token/channel secret.")
        return 'Invalid signature', 400
    except Exception as e:
        app.logger.error(f"Error in webhook: {str(e)}")
        return 'Internal server error', 500
    
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """メッセージ処理"""
    user_id = event.source.user_id
    message_text = event.message.text
    
    logger.info(f"User {user_id}: {message_text}")
    
    try:
        # AI競馬予想システムの実行
        if message_text.lower() in ['予想', '予想して', 'prediction', 'forecast']:
            response = ai_controller.execute_full_analysis()
            reply_message = format_prediction_response(response)
        
        elif message_text.lower() in ['ヘルプ', 'help', '使い方']:
            reply_message = get_help_message()
        
        elif message_text.lower().startswith('レース'):
            # 特定レースの予想
            race_info = extract_race_info(message_text)
            response = ai_controller.execute_race_analysis(race_info)
            reply_message = format_prediction_response(response)
        
        else:
            reply_message = "お疲れ様です！\n以下のコマンドが使用可能です：\n\n" \
                          "・「予想」：本日の予想を実行\n" \
                          "・「レース○○」：特定レースの予想\n" \
                          "・「ヘルプ」：使い方を表示"
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_message)
        )
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        error_message = "申し訳ございません。システムエラーが発生しました。\n" \
                       "しばらく時間をおいて再度お試しください。"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=error_message)
        )

@app.route('/scheduled-prediction', methods=['POST'])
def scheduled_prediction():
    """Cloud Scheduler からの定期実行"""
    try:
        logger.info("Scheduled prediction started")
        
        # AI競馬予想システム実行
        results = ai_controller.execute_daily_prediction()
        
        # 結果をLINEに配信
        if results:
            message = format_daily_prediction(results)
            broadcast_message(message)
            
        return jsonify({
            'status': 'success',
            'results': len(results) if results else 0,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in scheduled prediction: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

def format_prediction_response(response):
    """予想結果のフォーマット"""
    if not response or not response.get('predictions'):
        return "申し訳ございません。現在予想できるレースがありません。"
    
    message = "🏇 AI競馬予想結果 🏇\n\n"
    
    for prediction in response['predictions']:
        race_name = prediction.get('race_name', '不明')
        recommendations = prediction.get('recommendations', [])
        investment = prediction.get('investment', {})
        
        message += f"【{race_name}】\n"
        
        if recommendations:
            message += "◎本命：" + recommendations[0].get('horse_name', '不明') + "\n"
            if len(recommendations) > 1:
                message += "○対抗：" + recommendations[1].get('horse_name', '不明') + "\n"
            if len(recommendations) > 2:
                message += "▲単穴：" + recommendations[2].get('horse_name', '不明') + "\n"
        
        if investment:
            message += f"推奨投資額：{investment.get('total_amount', 0)}円\n"
            message += f"期待収益率：{investment.get('expected_return', 0):.1f}%\n"
        
        message += "\n"
    
    message += f"分析時刻：{datetime.now().strftime('%H:%M')}\n"
    message += "※投資は自己責任でお願いします"
    
    return message

def format_daily_prediction(results):
    """日次予想配信メッセージ"""
    message = "🌅 おはようございます！\n"
    message += "本日の競馬予想をお届けします。\n\n"
    
    total_races = len(results)
    total_investment = sum(r.get('investment', {}).get('total_amount', 0) for r in results)
    
    message += f"📊 本日の概要\n"
    message += f"予想レース数：{total_races}レース\n"
    message += f"総投資推奨額：{total_investment:,}円\n\n"
    
    for i, result in enumerate(results[:5], 1):  # 最大5レース表示
        race_name = result.get('race_name', f'第{i}レース')
        recommendations = result.get('recommendations', [])
        
        message += f"【{race_name}】\n"
        if recommendations:
            message += f"◎{recommendations[0].get('horse_name', '不明')}\n"
            if len(recommendations) > 1:
                message += f"○{recommendations[1].get('horse_name', '不明')}\n"
        message += "\n"
    
    if total_races > 5:
        message += f"...他{total_races-5}レース\n\n"
    
    message += "詳細は「予想」とメッセージしてください！\n"
    message += "Good luck! 🍀"
    
    return message

def broadcast_message(message):
    """全ユーザーにメッセージ配信"""
    try:
        # 実際の実装では、ユーザーIDのリストを管理する必要があります
        # ここでは簡単な例として、特定のユーザーIDに送信
        # line_bot_api.broadcast(TextSendMessage(text=message))
        logger.info(f"Broadcasting message: {message[:50]}...")
    except Exception as e:
        logger.error(f"Error broadcasting message: {str(e)}")

def get_help_message():
    """ヘルプメッセージ"""
    return """🏇 AI競馬予想システム v3.1 🏇

【使用方法】
・「予想」：本日の全レース予想
・「レース○○」：特定レースの詳細予想
・「ヘルプ」：この使い方を表示

【機能】
✅ 15段階の高精度分析
✅ 最適投資額自動算出
✅ リアルタイム情報収集
✅ 文字化け完全対策

【配信時間】
毎日 午前10:00 自動配信

投資は自己責任でお願いします。
Good luck! 🍀"""

def extract_race_info(message_text):
    """メッセージからレース情報を抽出"""
    # 簡単な実装例
    return {
        'race_number': None,
        'track': None,
        'distance': None
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
