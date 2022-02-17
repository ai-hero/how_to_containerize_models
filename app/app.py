# This file implements the flask endpoints for the model endpoints.
import json
from flask import Flask, jsonify, g
from flask_cors import CORS
from flask_expects_json import expects_json
from werkzeug.exceptions import HTTPException, UnprocessableEntity

from helpers.zero_shot_text_classifier import ZeroShotTextClassifier

# The flask api for serving predictions
app = Flask(__name__)
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
CORS(app)

# Expected JSON Schema of the predict request
with open("schema.json", "r") as f:
    SCHEMA = json.loads(f.read())


@app.errorhandler(HTTPException)
def handle_exception(e):
    """
    To keep all responses consistently JSON.
    Return JSON instead of HTML for HTTP errors.
    """
    return (
        jsonify(
            {
                "code": e.code,
                "name": e.name,
                "description": e.description,
            }
        ),
        e.code,
    )


@app.route("/", methods=["GET"])
@app.route("/ping", methods=["GET"])
@app.route("/health_check", methods=["GET"])
def health_check():
    """
    The healh check makes sure container is ok.
    For example, check the model, database connections (if present), etc.
    """
    # Warm-up the model with health check
    ZeroShotTextClassifier.load()
    return jsonify({"success": True}), 200


@app.route(
    "/predict",
    methods=["POST"],
)
@expects_json(SCHEMA)
def predict():
    """
    The main predict endpoint.
    """
    # Note: This is where you add authentication.

    # Payload is checked for the right schema using flask_expects_json
    # If payload is invalid, request will be aborted with error code 400
    # If payload is valid it is stored in g.data
    request_obj = g.data

    # We lift the request payload into the variables needed for prediction here.
    text = request_obj["text"]
    candidate_labels = request_obj["candidate_labels"]

    # You can add additional checks here, e.g. max number of classes, etc.
    if len(candidate_labels) > 5:
        raise UnprocessableEntity("This API allows for upto 5 classes.")

    # Get the prediction.
    # Note: You can add additional logic here as well, e.g. database look up, etc.
    prediction = ZeroShotTextClassifier.predict(
        text=text,
        candidate_labels=candidate_labels,
    )

    return jsonify(prediction)
