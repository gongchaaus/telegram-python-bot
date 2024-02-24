#!/usr/bin/env python
# pylint: disable=unused-argument
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

from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

import pandas as pd
import numpy as np

#MySql Setup
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

import mysql.connector

# Get database credentials from environment variables
mariadb_host = 'rdb-mariadb-gongcha-prod-read-01.cp9r0gu11n6n.ap-southeast-2.rds.amazonaws.com'
mariadb_port = '3306'
mariadb_user = 'GongChaAUData'
mariadb_password = 'Pamxf&7HmPCh9D'
mariadb_database = 'pxprodgongchaau'

# Engine for MariaDB
mariadb_connection_string = f"mysql+mysqlconnector://{mariadb_user}:{mariadb_password}@{mariadb_host}:{mariadb_port}/{mariadb_database}"
mariadb_engine = create_engine(mariadb_connection_string)


mysql_host = '34.116.84.145'
mysql_port = '3306'
mysql_user = 'gong-cha'
mysql_password = 'HelloGongCha2012'
mysql_database = 'gong_cha_redcat_db'

# Engine for MySQL
mysql_connection_string = f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
mysql_engine = create_engine(mysql_connection_string)

telegram_host = '34.116.84.145'
telegram_port = '3306'
telegram_user = 'python_telegram_bot'
telegram_password = 'HelloGongCha2012'
telegram_database = 'telegram_db'

# Engine for MySQL
telegram_connection_string = f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
telegram_engine = create_engine(mysql_connection_string)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    message = update.message
    chat_id = update.message.chat_id
    # upsert the user details into subscribes in telegram_db
    await update.message.reply_text(f'You\'re chat id is: {chat_id}\nPlease share your chat id with your manager')
    upsert_user_details(user, message)

# # used in /start # # 
async def upsert_user_details(user, message) -> None:
    upsert_query = '''
    INSERT INTO subscribers (chat_id, user_id, username, first_name, last_name, language_code, is_premium, added_to_attachment_menu)
    VALUES ({chat_id}, {user_id}, '{username}', '{first_name}', '{last_name}', '{language_code}', {is_premium}, {added_to_attachment_menu})
    ON DUPLICATE KEY UPDATE
        user_id = {user_id},
        username = '{username}',
        first_name = '{first_name}',
        last_name = '{last_name}',
        language_code = '{language_code}',
        is_premium = {is_premium},
        added_to_attachment_menu = {added_to_attachment_menu};
    '''.format(chat_id = message.chat_id, 
                user_id = user.id, 
                username = user.username if user.username else '', 
                first_name = user.first_name, 
                last_name = user.last_name if user.last_name else '',
                language_code = user.language_code if user.language_code else '',
                is_premium = True if user.is_premium else False,
                added_to_attachment_menu = True if user.added_to_attachment_menu else False
                )
    execute_stmt(upsert_query, telegram_engine)
    return upsert_query

def execute_stmt(stmt, engine):
    try:
        # Obtain a connection from the engine
        with engine.connect() as connection:
            # Start a new transaction
            with connection.begin():
                # Execute the provided statement
                connection.execute(text(stmt))
    except SQLAlchemyError as e:
        print(f"SQLAlchemyError occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")






def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6225546622:AAEUKdH5aK2IXhF_8IgefCtgFArDkRiOokk").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))


    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()