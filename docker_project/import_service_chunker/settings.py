import os

IMPORTS_FOLDER = os.getenv("IMPORT_FOLDER", "/imports/")
PROCESSED_FOLDER = os.getenv("PROCESSED_FOLDER", "/processed/")

KAFKA_SERVER = os.getenv("KAFKA_SERVER", "broker:9092")
KAFKA_OUTBOUND_TOPIC = os.getenv("KAFKA_OUTBOUND_TOPIC", "to_process")
