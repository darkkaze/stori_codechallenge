import logging
import os
from time import sleep

import sqlalchemy
from jinja2 import Environment, FileSystemLoader, select_autoescape
from kafka import KafkaConsumer
from kafka.admin import KafkaAdminClient
from kafka.errors import NoBrokersAvailable, NodeNotReadyError
from numpy import mean

from settings import (
    DB_DATABASE,
    DB_HOST,
    DB_PASSWORD,
    DB_USERNAME,
    KAFKA_INBOUND_TOPIC,
    KAFKA_SERVER,
    REPORT_FOLDER,
)

logging.basicConfig(filename="report.log", encoding="utf-8", level=logging.DEBUG)


def init_connection_engine():
    pool = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL.create(
            drivername="postgresql+psycopg2",
            username=DB_USERNAME,
            password=DB_PASSWORD,
            host=DB_HOST,
            database=DB_DATABASE,
        ),
        pool_size=5,
        max_overflow=2,
        pool_timeout=30,  # 30 seconds
        pool_recycle=1800,  # 30 minutes
    )
    return pool


db = init_connection_engine()

jinja2_env = Environment(
    loader=FileSystemLoader("templates"), autoescape=select_autoescape()
)


def main():
    """
    receive a account_id from kafka, then create a email report for the user.
    """
    consumer = KafkaConsumer(KAFKA_INBOUND_TOPIC, bootstrap_servers=[KAFKA_SERVER])
    for message in consumer:
        account_id = message.value.decode("utf-8")
        transactions_info = get_account_info(account_id)
        summary = get_summary(transactions_info)
        email_html = render_email(transactions_info, summary)
        send_email(transactions_info["email"], email_html)


def get_account_info(account_id: str) -> dict:
    """get account and transactions

    Args:
        account_id (str):

    Returns:
        dict: {"email", "first_name", "type", "transactions": ["transaction_ts", "transaction"]}

    """
    global db
    with db.connect().execution_options(autocommit=True) as conn:
        result = conn.execute(
            """
            SELECT email, first_name, type FROM accounts WHERE id=%s
            """,
            (account_id,),
        )
        row = result.fetchone()

        result = conn.execute(
            """
            SELECT transaction_ts, transaction FROM transactions WHERE account_id=%s ORDER BY transaction_ts
            """,
            (account_id,),
        )
        rows = result.fetchall()
        return {
            "email": row["email"],
            "first_name": row["first_name"],
            "type": row["type"],
            "transactions": [
                {
                    "transaction_ts": row["transaction_ts"],
                    "transaction": row["transaction"],
                }
                for row in rows
            ],
        }


def get_summary(transaction_info: dict) -> dict:
    """_summary_

    Args:
        transaction_info (dict):
            {"email", "first_name", "type", "transactions": ["transaction_ts", "transaction"]}


    Returns:
        dict: {"total_balance", "average", 1, 2, ..., 12}
    """
    summary = {
        "total_balance": round(
            sum([row["transaction"] for row in transaction_info["transactions"]]), 2
        ),
        "average": mean(
            [row["transaction"] for row in transaction_info["transactions"]]
        ),  # TODO:  average  with what parameters?
    }
    for month in range(1, 13):
        summary[month] = len(
            [
                row
                for row in transaction_info["transactions"]
                if row["transaction_ts"].month == month
            ]
        )
    return summary


def render_email(transaction_info: dict, summary: dict) -> str:
    """render email using jina2

    Args:
        transaction_info (dict):
            {"email", "first_name", "type", "transactions": ["transaction_ts", "transaction"]}
        summary (dict):
            {"total_balance", "average", 1, 2, ..., 12}

    Returns:
        str: rendered html
    """
    global jinja2_env
    template = jinja2_env.get_template("report.html")
    return str(template.render(transaction_info=transaction_info, summary=summary))


def send_email(email: str, html: str):
    """
    i dont have a email server,
    so i'm going to put the html in a report folder

    Args:
        email (str)
        html (str)  email content
    """
    with open(f"{REPORT_FOLDER}email_to_{email}.html", "w") as f:
        f.write(html)


def check_kafka():
    """
    check if kafka is ready
    notes:
        this process should not take responsibility of check if kafka is ready
        but it is in this form for practical purposes of a technical test.
    """
    while True:
        try:
            kafka_admin_client = KafkaAdminClient(bootstrap_servers=[KAFKA_SERVER])
            break
        except NoBrokersAvailable:
            logging.debug("kafka is not ready, waiting...")
            sleep(1)
        except NodeNotReadyError:
            logging.debug("kafka  node is not ready, waiting...")
            sleep(1)


if __name__ == "__main__":
    logging.debug("check if kafka is ready")
    check_kafka()
    logging.debug("starting")
    main()
