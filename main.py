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


import pymysql
pymysql.install_as_MySQLdb()

#Date & Time
from datetime import datetime, timedelta

#for making API calls
import http.client
import json


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
    message = update.message
    chat_id = update.message.chat_id
    # upsert the user details into subscribes in telegram_db
    await update.message.reply_text(f'You\'re chat id is: {chat_id}\nPlease share your chat id with your manager')
    upsert_user_details(user, message)

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
    user = update.effective_user
    message = update.message
    chat_id = update.message.chat_id
    # upsert the user details into subscribes in telegram_db
    await update.message.reply_text(f'You\'re chat id is: {chat_id}\nPlease share your chat id with your manager')
    upsert_user_details(user, message)
    
    store_id = get_user_store_id(chat_id)
    # await update.message.reply_text(f'Store ID: {store_id}')
    if store_id:
        shop_id, store_name = get_store_details(store_id)
        await update.message.reply_text(f'You have access to {store_name}')

        today = datetime.today()
        date_list = [today.date() - timedelta(days=x) for x in range(today.weekday())]
        # await update.message.reply_text(f'date_list size {len(date_list)}')

        for date in date_list:
            sales = get_daily_shop_sales(date,shop_id)
            target = get_daily_shop_target(date, store_id)
            await update.message.reply_text(f'{date}\nSales incl GST: ${sales},\nTarget is: ${target}')

    else:
        await update.message.reply_text(f'You have no acces to store sales,\nPlease ask your manager to add your chat id and Store ID')
  
    # TODO: add a context.job_queue.run_repeating
async def token(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    status, token = get_access_token()
    await update.message.reply_text(f'Status: {status} \nToken: {token}')

async def sales(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    store_id = get_user_store_id(chat_id)
    await update.message.reply_text(f'Store ID: {store_id}')
    # if store_id:
    #     shop_id, store_name = get_store_details(store_id)

    #     today = datetime.today()

    #     sales_val = get_daily_shop_sales(today, store_id)

    #     # end = start + timedelta(days=1)
    #     today_str = today.strftime("%Y-%m-%d")

    #     if(sales_val>0):

    #         await update.message.reply_text(f'{store_name} on {today_str}: ${sales_val} incl. GST')
    #     else:
    #         await update.message.reply_text(f'{store_name} has no sales on {today_str} yet')

    # else:
    #     await update.message.reply_text(f'You have no acces to store sales,\nPlease ask your manager to add your chat id and Store ID')

# async def sales(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     chat_id = update.effective_message.chat_id
#     # await update.message.reply_text(f'chat_id: {chat_id}')
#     store_id = get_user_store_id(chat_id)
#     # await update.message.reply_text(f'Store ID: {store_id}')
#     shop_id, _ = get_store_details(store_id)
#     # await update.message.reply_text(f'shop_id ID: {shop_id}')
#     date = datetime.today()
#     total_ex = get_daily_shop_sales(date,shop_id)
#     await update.message.reply_text(f'Today\'s Sales incl GST: ${total_ex*1.1}')


# # used in /start # # 
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
    with telegram_db.connect() as con:
        con.execute(upsert_query)

def get_user_store_id(chat_id) -> str:
    sheet_id = '1rqOeBjA9drmTnjlENvr57RqL5-oxSqe_KGdbdL2MKhM'
    sheet_name = 'Access'
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    access_df = pd.read_csv(url)   
    store_id =  access_df[(access_df['chat_id']== chat_id) & (access_df['Status']== 'Active')]['Store ID']
    return '' if store_id.size == 0 else store_id.values[0]

def get_store_details(store_id):
    sheet_id = '1ezyBlKquUhYnFwmIKTR4fghI59ZvGaKL35mKbcdeRy4'
    sheet_name = 'Stores'
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    store_df = pd.read_csv(url)
    shop_id = store_df[store_df['Store ID']== store_id]['shop_id']
    store_name = store_df[store_df['Store ID']== store_id]['Store Name']
    return shop_id.values[0], store_name.values[0]

def get_daily_shop_sales(date, recid_pol) -> float:
    start_datestr = date.strftime("%Y-%m-%d")
    # end_datestr = (date+timedelta(days=1)).strftime("%Y-%m-%d")
    # query = '''
    # SELECT *
    # FROM daily_shop_sales
    # WHERE shop_id = {recid_pol} and docket_date >='{start_datestr}' and docket_date <'{end_datestr}'
    # '''.format(recid_pol = recid_pol,start_datestr = start_datestr, end_datestr = end_datestr)
    query = '''
SELECT SUM(subtotal) as SUM
FROM  tbl_salesheaders tsh
WHERE txndate = '2024-02-24' AND recid_plo = 180
'''
    today_sales_df = pd.read_sql(query, mariadb_engine)
    return 0 if today_sales_df.size == 0 else today_sales_df.loc[0]['SUM']

def get_daily_shop_target(date, store_id) -> float:
    sheet_id = '1rqOeBjA9drmTnjlENvr57RqL5-oxSqe_KGdbdL2MKhM'
    sheet_name = 'Targets'
    url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    target_df = pd.read_csv(url)
    target_df['Date'] = pd.to_datetime(target_df['Date'])
    target =  target_df[(target_df['Store ID']== store_id) & (target_df['Date']== pd.to_datetime(date))]
    return 0 if target.size == 0 else target['Amount'].values[0]







def get_enrolled_store_ids() -> list:
  sheet_id = '1rqOeBjA9drmTnjlENvr57RqL5-oxSqe_KGdbdL2MKhM'
  sheet_name = 'Access'
  url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
  access_df = pd.read_csv(url)
  store_id =  access_df['Store ID']
  return [] if store_id.size == 0 else store_id.unique()


def get_enrolled_stores() -> list:
  store_ids = get_enrolled_store_ids()

  sheet_id = '1ezyBlKquUhYnFwmIKTR4fghI59ZvGaKL35mKbcdeRy4'
  sheet_name = 'Stores'
  url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
  store_df = pd.read_csv(url)

  store_df = store_df[(store_df['Store ID'].isin(store_ids))]
  return store_df


def get_batch_sales_df(start, end, shop_id_list):

    status, access_token = get_access_token()

    conn = http.client.HTTPSConnection("pos.aupos.com.au")
    payload = {
    "inputFields": {
        "dateDateValue_fld0_op": "greaterThanEqualTo",
        "dateDateValue_fld0_grp": "g1",
        "dateDateValue_fld0_value": start,
        "dateDateValue_fld1_op": "lessThan",
        "dateDateValue_fld1_grp": "g1",
        "dateDateValue_fld1_value": end,
        "storeProductStoreId_fld0_op": "in",
        "storeProductStoreId_fld0_grp": "g1",
        "storeProductStoreId_fld0_value": shop_id_list  # Include the list of strings with double quotes
    },
    "orderBy": "",
    "page": 1,
    "size": 1000
    }

    payload_json = json.dumps(payload)

    headers = {
    'Content-Type': 'application/json',
    'userTenantId': 'gc',
    'Authorization': f'Bearer {access_token}',
    'Cookie': 'JSESSIONID=0A7608CA4C2FB965C0EFE3CEB7E149F8.jvm1; OFBiz.Visitor=826825'
    }
    conn.request("POST", "/api/services/sales-summary", payload_json, headers)
    res = conn.getresponse()
    data = res.read()

    json_data = json.loads(data.decode("utf-8"))
    status = json_data["status"]
    sales = json_data["data"]["content"]
    sales_df = pd.DataFrame(sales)

    return status, payload_json, data, sales_df

def get_access_token():
    conn = http.client.HTTPSConnection("pos.aupos.com.au")
    payload = json.dumps({
    "username": "gc-admin",
    "password": "ofbiz"
    })
    headers = {
    'userTenantId': 'gc',
    'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
    'Content-Type': 'application/json'
    }
    conn.request("POST", "/api/auth/token", payload, headers)
    res = conn.getresponse()
    data = res.read()

    json_data = json.loads(data.decode("utf-8"))

    status = json_data["status"]
    access_token = json_data["data"]["access_token"]
    return status, access_token

def main() -> None:
    """Start the bot."""

    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6225546622:AAEUKdH5aK2IXhF_8IgefCtgFArDkRiOokk").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    
    # application.add_handler(CommandHandler("username", username))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.add_handler(CommandHandler("set", set_timer))
    application.add_handler(CommandHandler("unset", unset))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("sales", sales))
    application.add_handler(CommandHandler("token", token))

    job_queue = application.job_queue

    # TODO: get all subscribers and add context.job_queue.run_repeating to each subscriber
    # job_queue.run_repeating(callback_minute, interval=5, first=10)

    # Run the bot until the admin presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()