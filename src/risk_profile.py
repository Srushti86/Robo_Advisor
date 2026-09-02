def score_to_bucket(answers: dict) -> tuple:
    """
    Convert questionnaire answers into risk score (0-100) and bucket.

    answers: dict of question_id -> points, each 0-20
    returns: (score: int, bucket: str)
    """
    if not answers:
        raise ValueError("answers dict cannot be empty")

    total = sum(answers.values())
    max_possible = 20 * len(answers)
    score = round((total / max_possible) * 100)

    if score < 35:
        bucket = "Conservative"
    elif score < 65:
        bucket = "Moderate"
    else:
        bucket = "Aggressive"

    return score, bucket

# Answer -> point mappings used by the Streamlit UI
HORIZON_OPTIONS = ["<2 yrs", "2-5 yrs", "5-10 yrs", "10+ yrs"]
HORIZON_POINTS = [0, 7, 14, 20]

DRAWDOWN_OPTIONS = ["Sell everything", "Sell some", "Hold", "Buy more"]
DRAWDOWN_POINTS = [0, 7, 14, 20]

GOAL_OPTIONS = ["Capital preservation", "Income", "Growth", "Aggressive growth"]
GOAL_POINTS = [0, 7, 14, 20]