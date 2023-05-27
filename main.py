import os
import http

from flask import Flask, request
from werkzeug.wrappers import Response

from telegram import Bot, Update
from telegram.ext import Dispatcher, Filters, CommandHandler, MessageHandler, CallbackContext

app = Flask(__name__)

def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    update.message.reply_text(f"Your Telegram ID is: {user_id}")

def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)

bot = Bot(token=os.environ["BOT_TOKEN"])

dispatcher = Dispatcher(bot=bot, update_queue=None)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))

@app.post("/")
def index() -> Response:
    dispatcher.process_update(
        Update.de_json(request.get_json(force=True), bot))

    return "", http.HTTPStatus.NO_CONTENT
