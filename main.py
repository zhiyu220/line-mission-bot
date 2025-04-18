# LINE Bot - Flask 基礎架構設定
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os, json, base64
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)

# 初始化 Firebase
firebase_json = base64.b64decode(os.getenv("FIREBASE_CREDENTIALS_BASE64")).decode("utf-8")
cred_dict = json.loads(firebase_json)
cred = credentials.Certificate(cred_dict)
initialize_app(cred)

db = firestore.client()

# 環境變數（來自 Railway 或 .env）
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# 社團對照表（代替資料庫簡化版）
club_mapping = {
    "a8f2XjL9zQ": {"name": "吉他社", "type": "康樂性"},
    "entry_start": {"name": "入口說明", "type": "entry"}
    # ... 其他亂碼對照
}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip()

    if text.startswith("code:"):
        code = text.split(":")[1]
        if code in club_mapping:
            club = club_mapping[code]
            if club['type'] == "entry":
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="🎉 歡迎參加社評觀摩任務！掃描不同社團 QR 集點，集滿 5 點可得兌換券！")
                )
                return

            # 加入 Firebase 記錄邏輯...（略）
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"✅ 你已成功參觀【{club['name']}】（{club['type']}）")
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="❌ 無效的 QR Code 請重新掃描")
            )

if __name__ == "__main__":
    app.run()
