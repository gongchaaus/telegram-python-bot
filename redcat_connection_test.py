import pandas as pd

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

def return_stmt(stmt, engine):
    try:
        with engine.connect() as connection:
            result = connection.execute(text(stmt))
            return result.fetchone()
    except SQLAlchemyError as e:
        print(f"SQLAlchemyError error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

recid_plo = 150.0

today = pd.to_datetime('2024-01-31')
# await update.message.reply_text(f'today: {today}')
today_str = today.strftime("%Y-%m-%d")

query = '''
SELECT SUM(subtotal) as SUM
FROM  tbl_salesheaders tsh
WHERE txndate = '{date_str}' AND recid_plo = {recid_plo}
'''.format(recid_plo = recid_plo,date_str = today_str)

print(return_stmt(query, mariadb_engine))