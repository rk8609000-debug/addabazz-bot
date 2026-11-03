import os
import requests
from flask import Flask, request

app = Flask(__name__)

TOKEN = os.environ.get("BOT_TOKEN")
VIDEO_ID = os.environ.get("DEMO_VIDEO_FILE_ID")
URL = f"https://api.telegram.org/bot{TOKEN}/"

def send_message(chat_id, text, keyboard=None):
    data = {"chat_id": chat_id, "text": text}
    if keyboard:
        data["reply_markup"] = keyboard
    requests.post(URL + "sendMessage", json=data)

def send_video(chat_id):
    if VIDEO_ID:
        requests.post(URL + "sendVideo", json={
            "chat_id": chat_id,
            "video": VIDEO_ID,
            "caption": "Addabazz Demo Video"
        })
    else:
        send_message(chat_id, "Demo video is being prepared.")

@app.route("/", methods=["GET"])
def home():
    return "Addabazz Bot is Running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    update = request.json

    if "message" in update:
        msg = update["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")

        if text == "/start":
            send_message(
                chat_id,
                "Welcome to Addabazz Bot!\n\nChoose an option:",
                {
                    "inline_keyboard": [
                        [{"text": "Demo Video", "callback_data": "demo"}],
                        [{"text": "Premium Package", "callback_data": "package"}],
                        [{"text": "Payment", "callback_data": "payment"}]
                    ]
                }
            )
            send_video(chat_id)

        elif text == "/help":
            send_message(chat_id, "Welcome! Use /start to begin.")

        elif "video" in msg:
            file_id = msg["video"]["file_id"]
            send_message(chat_id, "Your video File ID:\n" + file_id)

    elif "callback_query" in update:
        query = update["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        data = query["data"]

        requests.post(URL + "answerCallbackQuery",
                      json={"callback_query_id": query["id"]})

        if data == "demo":
            send_video(chat_id)
        elif data == "package":
            send_message(chat_id, "6 Months: 300 BDT\n1 Year: 500 BDT")
        elif data == "payment":
            send_message(chat_id, "Payment: bKash and Nagad")

    return "OK"

if __name__ == "__main__":
    from threading import Thread
    import time

    def set_webhook():
        time.sleep(3)
        base = os.environ.get("RENDER_EXTERNAL_URL")
        if base:
            requests.post(URL + "setWebhook",
                          json={"url": base + "/webhook"})

    Thread(target=set_webhook, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
