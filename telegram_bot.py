import os
from telegram import Bot
from telegram.ext import CommandHandler

def start(update, context):
    user_id = update.effective_user.id
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your Telegram ID is: {user_id}")

def main():
    bot_token = os.getenv('BOT_TOKEN')
    bot = Bot(token=bot_token)
    dispatcher = bot.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    bot.polling()

if __name__ == '__main__':
    main()
