from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os

# 載入 .env
load_dotenv()

# 初始化 Firebase
cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# 初始化 LINE Bot
app = Flask(__name__)
line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    handler.handle(body, signature)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    text = event.message.text.strip().upper()

    if text.startswith("TASK_"):  # 任務代碼，如 TASK_GUITAR
        club_id = text.split("_")[1]
        ref = db.collection("points").document(f"{user_id}_{club_id}")
        if ref.get().exists:
            line_bot_api.reply_message(event.reply_token, TextSendMessage("你已完成這個社團任務囉！"))
        else:
            ref.set({"point": 1})
            # 計算目前總點數
            total = len([doc.id for doc in db.collection("points").where("user_id", "==", user_id).stream()])
            line_bot_api.reply_message(event.reply_token, TextSendMessage(f"✅ 完成 {club_id} 任務，已獲得 1 點！目前總點數：{total} 點"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
