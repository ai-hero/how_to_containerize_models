# This file implements the message queue for the model endpoints.
import os
import sys
import json
import redis
import logging
from dotenv import load_dotenv
from uuid import uuid4

load_dotenv("dev.env")

# Set up logger
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


def producer():
    # Connect to redis
    redis_url = os.environ.get("REDIS_URL")
    redis_connection = redis.Redis.from_url(redis_url)
    predict_request_topic = os.environ.get("PREDICT_REQUEST_TOPIC")

    # Create id for tracking our response
    _id = str(uuid4())

    # Send predict request
    log.info("Sending for predict request message: %s", _id)
    request_obj = {
        "text": "I am feeling great!",
        "candidate_labels": ["sad", "happy"],
        "id": _id,
    }
    redis_connection.lpush(predict_request_topic, json.dumps(request_obj))
