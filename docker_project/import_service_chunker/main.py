import logging
import os
import shutil
from io import BytesIO
from time import sleep
from typing import Iterable

import pandas as pd
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import NoBrokersAvailable, NodeNotReadyError, TopicAlreadyExistsError

from settings import (
    IMPORTS_FOLDER,
    KAFKA_OUTBOUND_TOPIC,
    KAFKA_SERVER,
    PROCESSED_FOLDER,
)

logging.basicConfig(filename="chunker.log", encoding="utf-8", level=logging.DEBUG)


def main():
    """
    Read the files from imports folder,
    chunk if by account and send it to a kafka topic to be proccessed
    """
    for df in discover_new_files():
        account_number_dfs = chunk_by_account_number(df)
        send_data_to_process(account_number_dfs)


def discover_new_files() -> Iterable[pd.DataFrame]:
    """check imports folder for new files
    open it in a dataframe and return a generator
    then  move the file to processed folder

    Returns:
        Iterable[pd.DataFrame]: Dataframe of a file
    """
    for file_name in os.listdir(IMPORTS_FOLDER):
        yield pd.read_csv(f"{IMPORTS_FOLDER}{file_name}")
        shutil.move(f"{IMPORTS_FOLDER}{file_name}", f"{PROCESSED_FOLDER}{file_name}")


def chunk_by_account_number(df: pd.DataFrame) -> Iterable[pd.DataFrame]:
    """
    chop a df by account_number operations

    Args:
        df [pd.DataFrame]: data of accounts operations to process

    Returns:
        Iterable[pd.DataFrame]: Dataframe of account_number operations

    Notes:
        For practical purposes i'm assuming that an account_number
        will not have more than 1mb operations (a kafka message)
    """
    account_numbers = df["account_number"].unique()
    for account_number in account_numbers:
        account_number_df = df[df["account_number"] == account_number].copy()
        yield account_number_df


def send_data_to_process(account_number_dfs: Iterable[pd.DataFrame]):
    """_summary_

    Args:
        account_number_dfs (Iterable[pd.DataFrame]):
            data of specific account number operations

    Notes:
        KafkaProducer.send() is asynchronous. When called it adds the record
        to a buffer of pending record sends and immediately returns
        so... is not necesary to add extra logic to reduce network latency
    """
    producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
    for account_number_df in account_number_dfs:
        file = BytesIO()
        account_number_df.to_csv(file)
        file.seek(0)
        producer.send(KAFKA_OUTBOUND_TOPIC, file.getvalue())


def create_topic_if_not_exist():
    """
    check if kafka is ready and check if the output topic exist

    notes:
        this process should not take responsibility of creating the topic in kafka,
        but it is in this form for practical purposes of a technical test.
    """
    while True:
        try:
            kafka_admin_client = KafkaAdminClient(bootstrap_servers=[KAFKA_SERVER])
            topic_list = [
                NewTopic(
                    name=KAFKA_OUTBOUND_TOPIC, num_partitions=1, replication_factor=1
                )
            ]
            kafka_admin_client.create_topics(topic_list)
            break
        except NoBrokersAvailable:
            logging.debug("kafka is not ready, waiting...")
            sleep(1)
        except NodeNotReadyError:
            logging.debug("kafka  node is not ready, waiting...")
            sleep(1)
        except TopicAlreadyExistsError:
            break


if __name__ == "__main__":
    logging.debug("check if kafka is ready")
    create_topic_if_not_exist()
    logging.debug("starting")
    while True:
        main()
        sleep(1)
