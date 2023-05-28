import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
print(sys.path)


import time
import flask
import telebot
import uuid
import json


# Set up telegram bot
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

# Set up flask
app = flask.Flask(__name__)

# Process webhook calls
# @app.route('/', methods=['POST'])
# def webhook():
#     if flask.request.headers.get('content-type') == 'application/json':
#         json_string = flask.request.get_data().decode('utf-8')

#         update = telebot.types.Update.de_json(json_string)
#         bot.process_new_updates([update])
#         return ('', 204)
#     else:
#         return ('Bad request', 400)

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message,
                 ("Hi there, I am stickersbot!\n\n"
                  "Please send me a picture of a person and I'll try my best to create a sticker!"))

# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    bot.reply_to(message, "Please send me a picture!")

@bot.message_handler(func= lambda message: True, content_types=['photo'])
def get_input_photo(message: telebot.types.Message):
    bot.reply_to(message, "Thank you for the photo! Please be patient while I create your sticker...")


if __name__ == '__main__':
    PORT = int(os.getenv("PORT")) if os.getenv("PORT") else 8080

    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)