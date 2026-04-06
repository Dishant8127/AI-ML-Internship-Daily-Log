import logging
import os

LOG_FILE_PATH = r"E:\AI-ML-Internship-Daily-Log\flask-ai-api\app.log"

logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def log_request(endpoint, text):
    logging.info(f"Endpoint: {endpoint} | Input: {text}")