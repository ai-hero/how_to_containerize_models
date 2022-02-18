# This file implements the message queue for the model endpoints.
import os
import sys
import json
import redis
import logging
from dotenv import load_dotenv

load_dotenv("dev.env")

# Set up logger
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


def consumer():
    # Connect to redis
    redis_url = os.environ.get("REDIS_URL")
    redis_connection = redis.Redis.from_url(redis_url)
    predict_response_topic = os.environ.get("PREDICT_RESPONSE_TOPIC")

    # Get response
    log.info("Waiting for predict response message...")
    _, msg = redis_connection.blpop(predict_response_topic)
    prediction = json.loads(msg)
    log.info("Prediction: %s", prediction)
