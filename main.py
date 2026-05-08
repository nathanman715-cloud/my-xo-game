import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ያንተን ቶክን እዚህ ጋር አስገባ
TOKEN = '8207112274:AAFtlY5nzzvtT4a87x3HcXgqd5No8IiKMx8'
bot = telebot.TeleBot(TOKEN)
games = {}

def check_winner(board):
    win_combinations = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
    for c in win_combinations:
        if board[c[0]] == board[c[1]] == board[c[2]] != " ":
            return board[c[0]]
    return "Draw" if " " not in board else None

def make_keyboard(board, include_invite=False):
    markup = types.InlineKeyboardMarkup(row_width=3)
    btns = [types.InlineKeyboardButton(board[i] if board[i] != " " else "⬜", callback_data=str(i)) for i in range(9)]
    markup.add(*btns)
    
    if include_invite:
        # ጓደኛ መጋበዣ በተን
        invite_btn = types.InlineKeyboardButton("👥 ጓደኛ ይጋብዙ", switch_inline_query="ና አብረን የቲክ-ታክ-ቶ (XO) ጨዋታ እንጫወት!")
        markup.row(invite_btn)
    
    return markup

@bot.message_handler(commands=['start', 'play'])
def start(message):
    games[message.chat.id] = {"board": [" " for _ in range(9)], "turn": "X", "active": True}
    bot.send_message(message.chat.id, "ቲክ-ታክ-ቶ ተጀምሯል! የ X ተራ ነው፡", reply_markup=make_keyboard(games[message.chat.id]["board"], include_invite=True))

@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    cid = call.message.chat.id
    if cid not in games or not games[cid]["active"]: return
    
    idx = int(call.data)
    if games[cid]["board"][idx] == " ":
        games[cid]["board"][idx] = games[cid]["turn"]
        res = check_winner(games[cid]["board"])
        
        if res:
            games[cid]["active"] = False
            msg = "አቻ!" if res == "Draw" else f"{res} አሸንፏል! 🎉"
            # ጨዋታው ሲያልቅ ድጋሚ መጫወቻ በተን መጨመር ይቻላል
            markup = make_keyboard(games[cid]["board"])
            restart_btn = types.InlineKeyboardButton("🔄 ድጋሚ ይጫወቱ", callback_data="restart")
            markup.row(restart_btn)
        else:
            games[cid]["turn"] = "O" if games[cid]["turn"] == "X" else "X"
            msg = f"የ {games[cid]['turn']} ተራ ነው፡"
            markup = make_keyboard(games[cid]["board"], include_invite=True)
            
        try:
            bot.edit_message_text(msg, cid, call.message.message_id, reply_markup=markup)
        except: pass

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
