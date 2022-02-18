# This file implements the message queue for the model endpoints.
import os
import sys
import json
import redis
import logging
import traceback
from uuid import uuid4
from jsonschema import validate, ValidationError
from helpers.zero_shot_text_classifier import ZeroShotTextClassifier

# Set up logger
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger(__name__)

# Expected JSON Schema of the predict request
with open("schema.json", "r") as f:
    SCHEMA = json.loads(f.read())


def predict(request_obj: dict):
    # Payload is checked for the right schema using flask_expects_json
    # If payload is invalid, request will be aborted with error code 400
    # If payload is valid it is stored in g.data

    # We lift the request payload into the variables needed for prediction here.
    text = request_obj["text"]
    candidate_labels = request_obj["candidate_labels"]

    # You can add additional checks here, e.g. max number of classes, etc.
    if len(candidate_labels) > 5:
        raise Exception("This service allows for upto 5 classes.")

    # Get the predictions.
    # Note: You can add additional logic here as well, e.g. database look up, etc.
    prediction = ZeroShotTextClassifier.predict(
        text=text,
        candidate_labels=candidate_labels,
    )
    return prediction


if __name__ == "__main__":
    redis_url = os.environ.get("REDIS_URL")
    redis_connection = redis.Redis.from_url(redis_url)
    predict_request_topic = os.environ.get("PREDICT_REQUEST_TOPIC")
    predict_response_topic = os.environ.get("PREDICT_RESPONSE_TOPIC")

    log.info("Warming up the model...")
    ZeroShotTextClassifier.load()
    while True:
        try:
            # Wait for predict request on request topic
            log.info("Waiting for predict request message...")
            _, msg = redis_connection.blpop(predict_request_topic)
            request_obj = json.loads(msg.decode("utf-8"))

            # We need an id so that our response message can include
            # the identifier. We extract it before the validation,
            # in order to send the error message in case the validation fails.
            _id = request_obj.get("id", str(uuid4()))

            # JSON Validation
            validate(instance=request_obj, schema=SCHEMA)

            # Predict
            prediction = predict(request_obj)

            # Create the response object
            prediction["id"] = _id

            # Push to the response topic
            redis_connection.lpush(predict_response_topic, json.dumps(prediction))
        except ValidationError as e:
            redis_connection.lpush(
                predict_response_topic, json.dumps({"id": _id, "error": f"{e}"})
            )
        except Exception as e2:  # pylint: disable=broad-except
            traceback.print_exc()
            redis_connection.lpush(
                predict_response_topic, json.dumps({"id": _id, "error": f"{e2}"})
            )
