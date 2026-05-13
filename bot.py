import telebot
import yt_dlp
import os
from flask import Flask
from threading import Thread

# --- Dummy Web Server (Render aur 24/7 Uptime ke liye) ---
app = Flask(__name__)
@app.route('/')
def home():
    return "Bot mast chal raha hai 24/7!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run_web)
    t.start()
# ---------------------------------------------------------

TOKEN = '8840124274:AAFJnT7Nge5uohGI_sE5Kw0z0y4q1v-Xlo0'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 Namaste! Mujhe koi bhi video link (YouTube, Instagram, Facebook, etc.) bhejo aur main use download karke dunga.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if not url.startswith('http'):
        bot.reply_to(message, "❌ Kripya ek valid video link bhejein.")
        return

    status_message = bot.reply_to(message, "⏳ Video download ho raha hai, kripya thoda intezaar karein...")

    try:
        ydl_opts = {
            'format': 'best[ext=mp4][filesize<50M]/best[filesize<50M]/best', 
            'outtmpl': 'downloaded_video_%(id)s.%(ext)s',
            'quiet': True,
            'noplaylist': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        bot.edit_message_text("⬆️ Video Telegram par upload ho raha hai...", chat_id=message.chat.id, message_id=status_message.message_id)
        
        with open(filename, 'rb') as video_file:
            bot.send_video(message.chat.id, video_file, caption="✅ Yeh lijiye aapka video!")
        
        os.remove(filename)
        bot.delete_message(chat_id=message.chat.id, message_id=status_message.message_id)

    except Exception as e:
        if "too large" in str(e).lower():
             bot.edit_message_text("❌ Yeh video 50MB se bada hai.", chat_id=message.chat.id, message_id=status_message.message_id)
        else:
             bot.edit_message_text("❌ Ek error aagaya. Kripya dusra link try karein.", chat_id=message.chat.id, message_id=status_message.message_id)
        try:
            for file in os.listdir():
                if file.startswith("downloaded_video_"):
                    os.remove(file)
        except:
            pass

# Pehle server start hoga, fir bot
keep_alive()
print("Bot chalu ho gaya hai! Telegram par jaakar test karein...")
bot.infinity_polling()

