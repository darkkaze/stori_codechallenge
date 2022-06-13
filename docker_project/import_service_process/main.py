import csv
import logging
import os
from io import BytesIO, StringIO
from time import sleep
from typing import List

import sqlalchemy
from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient
from kafka.errors import NoBrokersAvailable, NodeNotReadyError

from settings import KAFKA_INBOUND_TOPIC, KAFKA_OUTBOUND_TOPIC, KAFKA_SERVER
from tables import table_account_sql, table_transactions_sql

logging.basicConfig(filename="proccess.log", encoding="utf-8", level=logging.DEBUG)


def init_connection_engine():
    pool = sqlalchemy.create_engine(
        sqlalchemy.engine.url.URL.create(
            drivername="postgresql+psycopg2",
            username=os.getenv("DB_USERNAME"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_DATABASE"),
        ),
        pool_size=5,
        max_overflow=2,
        pool_timeout=30,  # 30 seconds
        pool_recycle=1800,  # 30 minutes
    )
    return pool


db = init_connection_engine()


def main():
    """
    receive a account operations csv from kafka, save it in to the db
    and push it to  report kafka topic
    """
    consumer = KafkaConsumer(KAFKA_INBOUND_TOPIC, bootstrap_servers=[KAFKA_SERVER])
    producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
    for message in consumer:
        reader = csv.DictReader(StringIO(message.value.decode("utf-8")))
        rows = [row for row in reader]
        if not rows:
            logging.warning("message without content?")
        account_id = get_or_create_account(
            rows[0]["account_number"],
            rows[0]["first_name"],
            rows[0]["last_name"],
            rows[0]["dob"],
            rows[0]["email"],
            rows[0]["type"],
        )
        insert_transactions(
            [
                (
                    row["operation_id"],
                    account_id,
                    row["transaction_ts"],
                    row["transaction"],
                )
                for row in rows
            ],
        )
        producer.send(KAFKA_OUTBOUND_TOPIC, bytes(str(account_id), "utf-8"))


def insert_transactions(transactions: List[List]):
    """bulk insert transactions

    Args:
        transactions (List[List]): [["operation_id", "account_id", "transaction_ts", "transaction"],]
    """
    global db
    with db.connect().execution_options(autocommit=True) as conn:
        result = conn.execute(
            """
            INSERT INTO transactions (id, account_id, transaction_ts, transaction)
            VALUES (%s,%s,%s,%s);
            """,
            transactions,
        )


def get_or_create_account(
    account_number: str,
    first_name: str,
    last_name: str,
    dob: str,
    email: str,
    type: str,
) -> str:
    """get or create account in db

    Args:
        account_number (str):
        first_name (str):
        last_name (str):
        dob (str):
        email (str):
        type (str):

    Returns:
        str: account_id

    Notes:
        I don't think that this type of process should create the accounts in the db
        but for this example works.
    """
    global db
    with db.connect().execution_options(autocommit=True) as conn:
        result = conn.execute(
            """
            SELECT id FROM accounts WHERE account_number=%s
            """,
            (account_number,),
        )
        row = result.fetchone()
        if row:
            return row["id"]
        result = conn.execute(
            """
            INSERT INTO accounts (account_number, first_name, last_name, dob, email, type)
            VALUES (%s,%s,%s,%s,%s,%s)  RETURNING id;
            """,
            (account_number, first_name, last_name, dob, email, type),
        )
        row = result.fetchone()
        return row["id"]


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


def create_table_if_not_exist():
    """
    notes:
        this process should not take responsibility of create tables.
        is just for practical purpose
    """
    global db
    with db.connect().execution_options(autocommit=True) as conn:
        conn.execute(table_account_sql)
        conn.execute(table_transactions_sql)


if __name__ == "__main__":
    logging.debug("check if kafka is ready")
    check_kafka()
    create_table_if_not_exist()
    logging.debug("starting")
    main()
