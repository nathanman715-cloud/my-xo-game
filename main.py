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

@bot.message_handler(commands=['start', 'play'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    invite_btn = types.InlineKeyboardButton("👥 ጓደኛ ይጋብዙ", switch_inline_query="play")
    markup.add(invite_btn)
    bot.send_message(message.chat.id, "ጓደኛህን ለመጋበዝ ከታች ያለውን በተን ተጫን፡", reply_markup=markup)

@bot.inline_handler(lambda query: query.query == 'play')
def query_text(inline_query):
    game_id = str(inline_query.from_user.id)
    # ተጫዋች 1 (X) ጨዋታውን የጀመረው ሰው ነው
    games[game_id] = {
        "board": [" " for _ in range(9)], 
        "turn": "X", 
        "active": True,
        "player_x": inline_query.from_user.id,
        "player_o": None # ሁለተኛው ተጫዋች ገና አልታወቀም
    }
    
    r = types.InlineQueryResultArticle(
        '1', 'ቲክ-ታክ-ቶ (XO) ጨዋታ',
        types.InputTextMessageContent(f"የ {inline_query.from_user.first_name} የቲክ-ታክ-ቶ ጨዋታ! የ X ተራ ነው፡"),
        reply_markup=make_keyboard(games[game_id]["board"], game_id)
    )
    bot.answer_inline_query(inline_query.id, [r], cache_time=1)

@bot.callback_query_handler(func=lambda call: call.data.startswith("play_"))
def handle_play(call):
    data = call.data.split("_")
    game_id = data[1]
    idx = int(data[2])
    user_id = call.from_user.id
    
    if game_id not in games or not games[game_id]["active"]:
        return

    game = games[game_id]

    # የ 'O' ተጫዋች ገና ካልተወሰነ እና የጀመረው ሰው ካልሆነ፣ እሱን 'O' አድርገው
    if game["player_o"] is None and user_id != game["player_x"]:
        game["player_o"] = user_id

    # ተራው የማን እንደሆነ ቼክ አድርግ
    current_player_id = game["player_x"] if game["turn"] == "X" else game["player_o"]

    if user_id != current_player_id:
        bot.answer_callback_query(call.id, "ተራው ያንተ አይደለም! ቆይ።", show_alert=True)
        return

    if game["board"][idx] == " ":
        game["board"][idx] = game["turn"]
        res = check_winner(game["board"])
        
        if res:
            game["active"] = False
            msg = "አቻ!" if res == "Draw" else f"አሸናፊ፡ {res} 🎉"
        else:
            game["turn"] = "O" if game["turn"] == "X" else "X"
            msg = f"የ {game['turn']} ተራ ነው፡"
            
        bot.edit_message_text(msg, inline_message_id=call.inline_message_id, reply_markup=make_keyboard(game["board"], game_id))
    else:
        bot.answer_callback_query(call.id, "ይህ ቦታ ተይዟል!")

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling()
