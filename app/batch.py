# This file implements the message queue for the model endpoints.
import os
import sys
import logging
import argparse
import pandas as pd
from tqdm import tqdm
from csv import DictWriter
from helpers.zero_shot_text_classifier import ZeroShotTextClassifier

# Set up logger
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger(__name__)


def predict(request_obj: dict):
    # Payload is checked for the right schema using flask_expects_json
    # If payload is invalid, request will be aborted with error code 400
    # If payload is valid it is stored in g.data

    # We lift the request payload into the variables needed for prediction here.
    text = request_obj["text"]
    candidate_labels = request_obj["candidate_labels"]

    # You can add additional checks here, e.g. max number of classes, etc.
    if len(candidate_labels) > 5:
        raise Exception("This API allows for upto 5 classes.")

    # Get the predictions.
    # Note: You can add additional logic here as well, e.g. database look up, etc.
    prediction = ZeroShotTextClassifier.predict(
        text=text,
        candidate_labels=candidate_labels,
    )
    return prediction


def valid_input_file(param: str) -> pd.DataFrame:
    base, ext = os.path.splitext(param)
    if ext.lower() not in (".csv"):
        raise argparse.ArgumentTypeError("Input file must have a .csv extension")
    if not os.path.exists(param):
        raise argparse.ArgumentTypeError("Input file does not exist.")
    try:
        df = pd.read_csv(param, encoding="UTF-8")
        if "text" not in df.columns:
            raise argparse.ArgumentTypeError(
                "Input csv does not contain a 'text' column."
            )
    except Exception as e:
        raise argparse.ArgumentTypeError(
            f"Could not load .csv - you need to pass a utf-8 encoded CSV file: {e}"
        ) from e
    return df


def valid_labels_file(param: str) -> pd.DataFrame:
    base, ext = os.path.splitext(param)
    if ext.lower() not in (".txt"):
        raise argparse.ArgumentTypeError("Labels file must have a .txt extension")
    if not os.path.exists(param):
        raise argparse.ArgumentTypeError("Labels file does not exist.")

    try:
        with open(param, "r", encoding="utf-8") as f:
            candidate_labels = [l.strip() for l in f.readlines()]
    except Exception as e:
        raise argparse.ArgumentTypeError(
            f"Could not load labels file. Please pass a utf-8 encoded txt file with each label on new line: {e}"
        ) from e

    # You can add additional checks here, e.g. max number of classes, etc.
    if len(candidate_labels) > 5:
        raise argparse.ArgumentTypeError(
            "This classifier only allows for upto 5 classes."
        )

    return candidate_labels


def valid_output_file(param: str) -> pd.DataFrame:
    base, ext = os.path.splitext(param)
    if ext.lower() not in (".csv"):
        raise argparse.ArgumentTypeError("Output file must have a .csv extension")
    if os.path.exists(param):
        raise argparse.ArgumentTypeError("Output file already exists.")
    return param


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l", "--labels", help="labels.txt file", type=valid_labels_file
    )
    parser.add_argument("-i", "--input", help="Input .csv file", type=valid_input_file)
    parser.add_argument(
        "-o", "--output", help="Output .csv file", type=valid_output_file
    )
    args = parser.parse_args()

    log.info("Warming up the model...")
    ZeroShotTextClassifier.load()

    df = args.input
    candidate_labels = args.labels
    output_file = args.output

    # predictions
    with open(output_file, "w", encoding="utf-8") as f:
        csv_writer = DictWriter(f, fieldnames=["text", "label", "score"])
        csv_writer.writeheader()
        for index, row in tqdm(df.iterrows(), total=df.shape[0]):
            try:
                prediction = ZeroShotTextClassifier.predict(
                    row["text"], candidate_labels=candidate_labels
                )
                # put the text in the prediction object
                prediction["text"] = row["text"]
                csv_writer.writerow(prediction)
            except Exception as e:  # pylint: disable=broad-except
                logging.error("Error in predicting line %d: %s", index, e)
