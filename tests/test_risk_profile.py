import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.risk_profile import score_to_bucket

def test_conservative():
    answers = {"q1":0, "q2": 0, "q3": 0}
    score, bucket = score_to_bucket(answers)
    assert bucket == "Conservative"
    assert score == 0

def test_aggressive():
    answers = {"q1": 20, "q2": 20, "q3": 20}
    score, bucket = score_to_bucket(answers)
    assert bucket == "Aggressive"
    assert score == 100

def test_moderate():
    answers = {"q1": 10, "q2": 10, "q3": 10}
    score, bucket = score_to_bucket(answers)
    assert bucket == "Moderate"

def test_empty_raises():
    try:
        score_to_bucket({})
        assert False, "should have raised"
    except ValueError:
        pass