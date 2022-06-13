import os

KAFKA_SERVER = os.getenv("KAFKA_SERVER", "broker:9092")
KAFKA_INBOUND_TOPIC = os.getenv("KAFKA_INBOUND_TOPIC", "to_report")

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_DATABASE = os.getenv("DB_DATABASE")


REPORT_FOLDER = os.getenv("REPORT_FOLDER", "/reports/")
