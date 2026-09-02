import os
import streamlit as st
import json
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Open a new MySQL connection - uses Streamlit secrets on Streamlit Cloud, falls back to .env locally"""
    try:
        return mysql.connector.connect(
            host=st.secrets["DB_HOST"],
            port=st.secrets["DB_PORT"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            database=st.secrets["DB_NAME"],
        )
    except (KeyError, FileNotFoundError):
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "3306"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "robo_advisor"),
        )

def get_or_create_user(username: str) -> int:
    """Return the user's id, creating the user row if it doesn't exist yet."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        row = cursor.fetchone()
        if row:
            return row[0]

        cursor.execute("INSERT INTO users (username) VALUES (%s)", (username,))
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

def save_risk_profile(user_id: int, score: int, bucket: str) -> int:
    """Insert a risk profile row and return its id."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO risk_profiles (user_id, score, bucket) VALUES (%s, %s, %s)", 
            (user_id, score, bucket),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

def save_recommendation(risk_profile_id: int, weights: dict, metrics: dict) -> int:
    """
    Insert a portfolio recommendation row.
    metrics: dict with keys sharpe, sortino, volatility, max_drawdown, diversification
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO portfolio_recommendations
                (risk_profile_id, weights_json, sharpe_ratio, sortino_ratio,
                annualized_volatility, max_drawdown, diversification_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (
                risk_profile_id,
                json.dumps(weights),
                metrics.get("sharpe"),
                metrics.get("sortino"),
                metrics.get("volatility"),
                metrics.get("max_drawdown"),
                metrics.get("diversification")
            ),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.cursor()

def get_user_history(username: str) -> list:
    """
    Return every past risk profile + recommendation for a user,
    most recent first. Each row is a dict.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT
                rp.id AS risk_profile_id,
                rp.score,
                rp.bucket,
                rp.created_at AS profile_date,
                pr.weights_json,
                pr.sharpe_ratio,
                pr.sortino_ratio,
                pr.annualized_volatility,
                pr.max_drawdown,
                pr.diversification_score,
                pr.created_at AS recommendation_date
            FROM risk_profiles rp 
            JOIN users u ON rp.user_id = u.id
            LEFT JOIN portfolio_recommendations pr 
                ON pr.risk_profile_id = rp.id
            WHERE u.username = %s
            ORDER BY rp.created_at DESC""",
        (username,),
        )
        rows = cursor.fetchall()
        for r in rows:
            if r["weights_json"]:
                r["weights"] = json.loads(r["weights_json"])
        return rows
    finally:
        cursor.close()
        conn.close()

def test_connection() -> bool:
    """Quick sanity check you can run standalone: python src/db.py"""
    try:
        conn = get_connection()
        conn.close()
        return True
    except Error as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    if test_connection():
        print("Connected to MySQL successfully.")
    else:
        print("Could not connect - check your .env credentials and that MySQL is running.")