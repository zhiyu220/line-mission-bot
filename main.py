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
  "W9ZplJPSRB": {
    "name": "AIESEC元智分會",
    "type": "學術文藝性"
  },
  "Zj4MEBEGFC": {
    "name": "攝影社",
    "type": "學術文藝性"
  },
  "tkJy7A81c8": {
    "name": "圍棋社",
    "type": "學術文藝性"
  },
  "RDPN7sEVML": {
    "name": "證券研習社",
    "type": "學術文藝性"
  },
  "pdBPIob4yM": {
    "name": "CPA Club",
    "type": "學術文藝性"
  },
  "0iFVTCcJOC": {
    "name": "烘焙社",
    "type": "學術文藝性"
  },
  "Taj47ICVfu": {
    "name": "新世紀領袖培育計畫團",
    "type": "學術文藝性"
  },
  "QLfeYD3c4O": {
    "name": "資訊研究社",
    "type": "學術文藝性"
  },
  "EOakHXDGRn": {
    "name": "桌上遊戲社",
    "type": "學術文藝性"
  },
  "GtCgBRjeWR": {
    "name": "自造者社(機器人研究社)",
    "type": "學術文藝性"
  },
  "PRmNJDYeGe": {
    "name": "遊戲創作社",
    "type": "學術文藝性"
  },
  "ADW4av1WYR": {
    "name": "管理顧問社",
    "type": "學術文藝性"
  },
  "NUo0Bf4zg6": {
    "name": "卡牌社",
    "type": "學術文藝性"
  },
  "wDNaFjpIZW": {
    "name": "競技程式人才培育社",
    "type": "學術文藝性"
  },
  "QSoGJkXdod": {
    "name": "生命泉學生教會",
    "type": "聯誼性"
  },
  "H0jB8cJX6D": {
    "name": "越南學生聯誼會",
    "type": "聯誼性"
  },
  "lWLqJz12Fl": {
    "name": "閱人社",
    "type": "聯誼性"
  },
  "BHkYWnaYOP": {
    "name": "原青社",
    "type": "聯誼性"
  },
  "DG4kY5PU5l": {
    "name": "光鹽唱詩社",
    "type": "聯誼性"
  },
  "Z0JkB258bG": {
    "name": "熱舞社",
    "type": "康樂性"
  },
  "u0WRpgXjnT": {
    "name": "流行音樂錄影帶舞蹈社",
    "type": "康樂性"
  },
  "bfBfvSEXPg": {
    "name": "MIDI熱音社",
    "type": "康樂性"
  },
  "aQMDrPdooj": {
    "name": "管樂社",
    "type": "康樂性"
  },
  "2oxuR9lKUa": {
    "name": "吉他社",
    "type": "康樂性"
  },
  "CyF4b9tSAw": {
    "name": "弦樂社",
    "type": "康樂性"
  },
  "BFt6t4aoz2": {
    "name": "流行音樂錄音社",
    "type": "康樂性"
  },
  "5nvb8Mv0uB": {
    "name": "鋼琴社",
    "type": "康樂性"
  },
  "CYWDMBJx03": {
    "name": "Disc Jockey 社",
    "type": "康樂性"
  },
  "D6QSExxBR7": {
    "name": "嘻哈文化研究社",
    "type": "康樂性"
  },
  "gCEj6E7lPb": {
    "name": "崇德青年志工社",
    "type": "服務性"
  },
  "x1Lpx1pYqP": {
    "name": "動物關懷社",
    "type": "服務性"
  },
  "G6AgY9Qjwg": {
    "name": "中智社",
    "type": "服務性"
  },
  "9L2w47ftRy": {
    "name": "IC部落社",
    "type": "服務性"
  },
  "k9cQvY4nIf": {
    "name": "跆拳道社",
    "type": "體育性"
  },
  "okNf4twVP4": {
    "name": "柔道社",
    "type": "體育性"
  },
  "OjAy2nzG7k": {
    "name": "劍道社",
    "type": "體育性"
  },
  "dhi5vl5gco": {
    "name": "棒球社",
    "type": "體育性"
  },
  "br9CkTHFz8": {
    "name": "排球社",
    "type": "體育性"
  },
  "xUnFtNCwvL": {
    "name": "長拳社",
    "type": "體育性"
  },
  "tRQUSEcOxa": {
    "name": "滑板社",
    "type": "體育性"
  },
  "kwNkPodduo": {
    "name": "登山社",
    "type": "體育性"
  },
  "nZkQKZnwTN": {
    "name": "足球社",
    "type": "體育性"
  },
  "VBv4xHvOki": {
    "name": "擊劍社",
    "type": "體育性"
  },
  "SI1jY5muMw": {
    "name": "學生會",
    "type": "自治性"
  },
  "fwD05vrbyf": {
    "name": "電機系乙組學會",
    "type": "自治性"
  },
  "Ql7yImK8xK": {
    "name": "電機系丙組學會",
    "type": "自治性"
  },
  "wpBbptBrbe": {
    "name": "電通英專班學會",
    "type": "自治性"
  },
  "Ufh3C5edFp": {
    "name": "化材系學會",
    "type": "自治性"
  },
  "cvdLZpgsaB": {
    "name": "工管系學會",
    "type": "自治性"
  },
  "MOFOBNDITs": {
    "name": "資工系學會",
    "type": "自治性"
  },
  "zEasvAwnbY": {
    "name": "資管系學會",
    "type": "自治性"
  },
  "JH8vpMxbSP": {
    "name": "資傳系學會",
    "type": "自治性"
  },
  "1Jx3PTFOCn": {
    "name": "資訊英專班學會",
    "type": "自治性"
  },
  "zFonEZlDyE": {
    "name": "財金班學會",
    "type": "自治性"
  },
  "iQqMqd26aF": {
    "name": "國企班學會",
    "type": "自治性"
  },
  "Wy1Ze66Pcb": {
    "name": "會計班學會",
    "type": "自治性"
  },
  "NVNuAYpBfd": {
    "name": "管理學院英語專班",
    "type": "自治性"
  },
  "8QGYDwDvhK": {
    "name": "應外系學會",
    "type": "自治性"
  },
  "gdfCZ9n2XM": {
    "name": "中語系學會",
    "type": "自治性"
  },
  "hpnIxo4Ewn": {
    "name": "人社英專班學會",
    "type": "自治性"
  },
  "As7HI2w4oY": {
    "name": "男生宿舍自治會",
    "type": "自治性"
  },
  "GuPTGvlOgb": {
    "name": "女生宿舍自治會",
    "type": "自治性"
  },
  "18fRsdk2hO": {
    "name": "輔導義工",
    "type": "義工性"
  },
  "bS8YVDLaUo": {
    "name": "衛保義工",
    "type": "義工性"
  },
  "8vkD9MeTH9": {
    "name": "生活尖兵",
    "type": "義工性"
  },
  "eiTtQeHumP": {
    "name": "YOUTH志工大聯盟",
    "type": "義工性"
  },
  "FmzjiGyhDB": {
    "name": "元智大使",
    "type": "義工性"
  }
}

@app.route("/callback", methods=["GET"])
def handle_qr_scan():
    code = request.args.get("code")
    if code in club_mapping:
        club = club_mapping[code]
        return f"✅ 你已成功參觀【{club['name']}】（{club['type']}）"
    else:
        return "❌ 無效的 QR Code"

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

            user_ref = db.collection("users").document(user_id)

            user_data = user_ref.get().to_dict() or {}
            points = user_data.get("points", {})
            completed = user_data.get("completed", {})

            club_type = club["type"]
            visited_count = points.get(club_type, 0)

            if visited_count < 5:
                points[club_type] = visited_count + 1
                user_ref.set({"points": points}, merge=True)

            reply = f"✅ 你已成功參觀【{club['name']}】（{club['type']}）\n目前進度：{points[club_type]}/5 點"

            # 滿點觸發卡片
            if points[club_type] == 5 and not completed.get(club_type):
                completed[club_type] = True
                user_ref.set({"completed": completed}, merge=True)
                reply += f"\n🎉 恭喜完成「{club_type}」任務！已獲得兌換券！"

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
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
