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
telegram_connection_string = f"mysql+mysqlconnector://{telegram_user}:{telegram_password}@{telegram_host}:{telegram_port}/{telegram_database}"
telegram_engine = create_engine(telegram_connection_string)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    message = update.message
    chat_id = update.message.chat_id
    # upsert the user details into subscribes in telegram_db
    upsert_query = upsert_user_details(user, message)
    await update.message.reply_text(f'You\'re chat id is: {chat_id}\nPlease share your chat id with your manager')

def upsert_user_details(user, message) -> None:
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


async def sales(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    store_id = check_user_store_access(chat_id)
    # await update.message.reply_text(f'Store ID: {store_id}')

    if store_id:
        recid_plo, store_name = get_store_details(store_id)
        # await update.message.reply_text(f'recid_pol: {recid_pol}')
        # await update.message.reply_text(f'store_name: {store_name}')
        # today = pd.to_datetime('today')
        today = pd.to_datetime('2024-02-14')
        await update.message.reply_text(f'today: {today}')
        today_str = today.strftime("%Y-%m-%d")

        query = '''
SELECT SUM(subtotal) as SUM
FROM  tbl_salesheaders tsh
WHERE txndate = '{date_str}' AND recid_plo = {recid_plo}
'''.format(recid_plo = recid_plo,date_str = today_str)
        
        await update.message.reply_text(f'query: {query}')

        today_sales_df = pd.read_sql(query, mariadb_engine)
        await update.message.reply_text(f'today_sales_df: {today_sales_df}')
        # sales_val = get_store_sales(today, recid_plo)
        # await update.message.reply_text(f'sales_val: {sales_val}')
        

        # if(sales_val>0):
        #     await update.message.reply_text(f'{store_name} on {today_str}: ${sales_val} incl. GST')

        # else:
        #     await update.message.reply_text(f'{store_name} has no sales on {today_str} yet')

    else:
        await update.message.reply_text(f'You have no acces to store sales,\nPlease ask your manager to add your chat id and Store ID')



def check_user_store_access(chat_id) -> str:
    sheet_id = '1rqOeBjA9drmTnjlENvr57RqL5-oxSqe_KGdbdL2MKhM'
    sheet_name = 'Access'
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    access_df = pd.read_csv(url)   
    store_id =  access_df[(access_df['chat_id']== chat_id) & (access_df['Status']== 'Active')]['Store ID']
    return '' if store_id.size == 0 else store_id.values[0]

def get_store_details(store_id):
    sheet_id = '1peA8effpeSTk3duIjxF46V-PrDD8tv3fubTCDEpD940'
    sheet_name = 'Stores'
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    store_df = pd.read_csv(url)
    recid_plo = store_df[store_df['Store ID']== store_id]['recid_plo']
    store_name = store_df[store_df['Store ID']== store_id]['Store Name']
    return recid_plo.values[0], store_name.values[0]

def get_store_sales(date, recid_plo) -> float:
    date_str = date.strftime("%Y-%m-%d")
    query = '''
SELECT SUM(subtotal) as SUM
FROM  tbl_salesheaders tsh
WHERE txndate = '{date_str}' AND recid_plo = {recid_plo}
'''.format(recid_plo = recid_plo,date_str = date_str)
    return query
    # today_sales_df = pd.read_sql(query, mariadb_engine)
    # return 0 if today_sales_df.empty else today_sales_df.loc[0]['SUM']





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
    application.add_handler(CommandHandler("sales", sales))


    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()