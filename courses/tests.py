from django.test import TestCase
from courses.utils import get_match_score

class FuzzyMatchingTests(TestCase):
    def test_exact_match(self):
        self.assertAlmostEqual(get_match_score("Python", "Python"), 1.0)

    def test_partial_match(self):
        self.assertTrue(get_match_score("Pyton", "Python") > 0.85)

    def test_low_match(self):
        self.assertTrue(get_match_score("Java", "Python") < 0.5)

