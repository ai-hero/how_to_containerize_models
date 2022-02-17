from unittest import TestCase
from helpers.zero_shot_text_classifier import ZeroShotTextClassifier


class ZeroShotTestCase(TestCase):
    def setUp(self):
        ZeroShotTextClassifier.load()

    def test_default_widget_size(self):
        prediction = ZeroShotTextClassifier.predict("This is great!", ["sad", "happy"])
        self.assertEqual(prediction["label"], "happy")
        self.assertGreaterEqual(prediction["score"], 0.9)
