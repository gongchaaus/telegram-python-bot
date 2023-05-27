from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Define a function to handle the /hello command
def hello(update, context):
    user_id = update.effective_user.id
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your Telegram ID is: {user_id}")

def main():
    # Initialize the Telegram bot
    updater = Updater(token='YOUR_BOT_TOKEN', use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Register the command handler
    hello_handler = CommandHandler('hello', hello)
    dispatcher.add_handler(hello_handler)

    # Start the bot
    updater.start_polling()

    # Keep the bot running until interrupted
    updater.idle()

if __name__ == '__main__':
    main()
