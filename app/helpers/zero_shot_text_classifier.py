import sys
from transformers import pipeline
from typing import List
import numpy as np
from time import perf_counter
import logging

# Set up logger
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger(__name__)


class ZeroShotTextClassifier:
    """Class with only class methods"""

    # Class variable for the model pipeline
    classifier = None

    @classmethod
    def load(cls):
        # Only load one instance of the model
        if cls.classifier is None:
            # Load the model pipeline.
            # Note: Usually, this would also download the model.
            # But, we download the model into the container in the Dockerfile
            # so that it's built into the container and there's no download at
            # run time (otherwise, each time we'll download a 1.5GB model).
            # Loading still takes time, though. So, we do that here.
            # Note: You can use a GPU here if needed.
            t0 = perf_counter()
            cls.classifier = pipeline(
                "zero-shot-classification", model="facebook/bart-large-mnli"
            )
            elapsed = 1000 * (perf_counter() - t0)
            log.info("Model warm-up time: %d ms.", elapsed)

    @classmethod
    def predict(cls, text: str, candidate_labels: List[str]):
        assert len(candidate_labels) > 0

        # Make sure the model is loaded
        cls.load()

        # For the tutorial, let's create
        # a custom object from the huggingface prediction.
        # Our prediction object will include the label and score

        t0 = perf_counter()
        # pylint: disable-next=not-callable
        huggingface_predictions = cls.classifier(text, candidate_labels)
        elapsed = 1000 * (perf_counter() - t0)
        log.info("Model prediction time: %d ms.", elapsed)

        # Create the custom prediction object.
        max_index = np.argmax(huggingface_predictions["scores"])
        label = huggingface_predictions["labels"][max_index]
        score = huggingface_predictions["scores"][max_index]
        return {"label": label, "score": score}
