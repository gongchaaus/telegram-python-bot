#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

import pandas as pd

#MySql Setup
from sqlalchemy import create_engine
import pymysql
pymysql.install_as_MySQLdb()

#Date & Time
from datetime import datetime, timedelta


gong_cha_db = create_engine('mysql://python_telegram_bot:HelloGongCha2012@34.116.84.145:3306/gong_cha_db')
telegram_db = create_engine('mysql://python_telegram_bot:HelloGongCha2012@34.116.84.145:3306/telegram_db')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

# async def username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Send the user's mobile number when the command /mobile is issued."""
#     user = update.effective_user
#     username = user.username if user.username else "Not available"
#     await update.message.reply_text(f"Your username is: {username}")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

async def alarm(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the alarm message."""
    job = context.job
    await context.bot.send_message(job.chat_id, text=f"Beep! {job.data} seconds are over!")

def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


async def set_timer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id

    try:
        # args[0] should contain the time for the timer in seconds
        due = float(context.args[0])
        if due < 0:
            await update.effective_message.reply_text("Sorry we can not go back to future!")
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_repeating(alarm, due, chat_id=chat_id, name=str(chat_id), data=due)

        text = "Timer successfully set!"
        if job_removed:
            text += " Old one was removed."
        await update.effective_message.reply_text(text)

    except (IndexError, ValueError):
        await update.effective_message.reply_text("Usage: /set <seconds>")


async def unset(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "Timer successfully cancelled!" if job_removed else "You have no active timer."
    await update.message.reply_text(text)

#chat_id :6282871705
async def callback_minute(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=6282871705, text='One message every minute')

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """subscribe user on to the bi-daily sales broadcast"""
    #check whehter user has username
    user = update.effective_user

    if user.username:
        #check whether the user has subscribed
        user_query = '''
        select *
        from subscribers
        where username = '{username}'
        '''.format(username = user.username)
        user_df = pd.read_sql(user_query, telegram_db)
        print(user_df)

        #add the user details on to subscribes in telegram_db

        #send the message to confirm the user
        message = f"@{user.username} subscribed"
        await update.message.reply_text(message)

    else:
        message = "Please obtain a Telegran Username in Setting -> Edit -> Username"
        #send the message to prompt the user to assign an username
        await update.message.reply_text(message)

async def sales(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    today= datetime.today().strftime('%Y-%m-%d')
    tomorrow = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    query = '''
        select *
        from daily_shop_sales
        where shop_id = 31 and docket_date >= '{start}' and docket_date < '{end}'
        '''.format(start=today, end = tomorrow)
    data = pd.read_sql(query, gong_cha_db)
    total_ex = 0 if data.empty else data['total_ex'].values[0]
    await update.message.reply_text(f'Regent Place Today\'s Net Sales: ${total_ex}')


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6024150435:AAGWufEQ00Sgdglcdy8Mfsx_msapPK9pkz8").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    
    # application.add_handler(CommandHandler("username", username))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.add_handler(CommandHandler("set", set_timer))
    application.add_handler(CommandHandler("unset", unset))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("sales", sales))

    # job_queue = application.job_queue
    # job_queue.run_repeating(callback_minute, interval=5, first=10)

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()