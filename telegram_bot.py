import os
from telegram.ext import Updater, CommandHandler

def start(update, context):
    user_id = update.effective_user.id
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your Telegram ID is: {user_id}")

def main():
    token = os.getenv('BOT_TOKEN')
    port = int(os.getenv('PORT', 8080))

    updater = Updater(token=token, use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    # Start the bot and listen on the provided port
    updater.start_webhook(listen='0.0.0.0', port=port, url_path=token)
    updater.bot.setWebhook(f"https://your-cloud-run-service-url/{token}")

if __name__ == '__main__':
    main()
