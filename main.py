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

TOKEN = '8207112274:AAFtlY5nzzvtT4a87x3HcXgqd5No8IiKMx8'
bot = telebot.TeleBot(TOKEN)
games = {}

def check_winner(board):
    win_combinations = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
    for c in win_combinations:
        if board[c[0]] == board[c[1]] == board[c[2]] != " ":
            return board[c[0]]
    return "Draw" if " " not in board else None

def make_keyboard(board, game_id):
    markup = types.InlineKeyboardMarkup(row_width=3)
    btns = [types.InlineKeyboardButton(board[i] if board[i] != " " else "⬜", callback_data=f"play_{game_id}_{i}") for i in range(9)]
    markup.add(*btns)
    return markup

# ጓደኛን ለመጋበዝ
@bot.message_handler(commands=['start', 'play'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    invite_btn = types.InlineKeyboardButton("👥 ጓደኛ ይጋብዙ", switch_inline_query="play")
    markup.add(invite_btn)
    bot.send_message(message.chat.id, "ጓደኛህን ለመጋበዝ ከታች ያለውን በተን ተጫን፡", reply_markup=markup)

# Inline Query ሲላክ (ጓደኛህ ሲጋበዝ)
@bot.inline_handler(lambda query: query.query == 'play')
def query_text(inline_query):
    try:
        game_id = str(inline_query.from_user.id)
        games[game_id] = {"board": [" " for _ in range(9)], "turn": "X", "active": True}
        
        r = types.InlineQueryResultArticle(
            '1', 'ቲክ-ታክ-ቶ (XO) ጨዋታ',
            types.InputTextMessageContent(f"የ {inline_query.from_user.first_name} የቲክ-ታክ-ቶ ጨዋታ ተጀምሯል! የ X ተራ ነው፡"),
            reply_markup=make_keyboard(games[game_id]["board"], game_id)
        )
        bot.answer_inline_query(inline_query.id, [r])
    except Exception as e:
        print(e)

@bot.callback_query_handler(func=lambda call: call.data.startswith("play_"))
def handle_play(call):
    data = call.data.split("_")
    game_id = data[1]
    idx = int(data[2])
    
    if game_id not in games or not games[game_id]["active"]: return
    
    if games[game_id]["board"][idx] == " ":
        games[game_id]["board"][idx] = games[game_id]["turn"]
        res = check_winner(games[game_id]["board"])
        
        if res:
            games[game_id]["active"] = False
            msg = "አቻ!" if res == "Draw" else f"{res} አሸንፏል! 🎉"
        else:
            games[game_id]["turn"] = "O" if games[game_id]["turn"] == "X" else "X"
            msg = f"የ {games[game_id]['turn']} ተራ ነው፡"
            
        bot.edit_message_text(msg, inline_message_id=call.inline_message_id, reply_markup=make_keyboard(games[game_id]["board"], game_id))

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
