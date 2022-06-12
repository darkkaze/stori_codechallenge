import os

IMPORTS_FOLDER = os.getenv("IMPORT_FOLDER", "/imports/")

KAFKA_SERVER = os.getenv("KAFKA_SERVER", "broker:9092")
KAFKA_OUTPUT_TOPIC = os.getenv("KAFKA_OUTPUT_TOPIC", "to_process")
