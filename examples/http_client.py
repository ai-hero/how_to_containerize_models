# This file implements the message queue for the model endpoints.
import os
import sys
import logging
import requests
from dotenv import load_dotenv

load_dotenv("dev.env")

# Set up logger
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


def get_a_prediction():
    # Connect to redis
    server_url = os.environ.get("SERVER_URL")

    # Send predict request
    log.info("Making a predict request:")
    request_obj = {
        "text": "I am feeling great!",
        "candidate_labels": ["sad", "happy"],
    }
    resp = requests.post(f"{server_url}/predict", json=request_obj)
    resp.raise_for_status()

    prediction = resp.json()
    logging.info("Got prediction %s", prediction)


if __name__ == "__main__":
    # Ideally these would be your logic
    # on the flow of the data, before and after
    # prediction.
    get_a_prediction()
