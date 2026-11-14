import sqlite3
import json
import hashlib
import os

from datetime import datetime, timedelta


# DATABASE LOCATION
DATABASE = "data/cache.db"


# CREATE DATABASE AND TABLE
def initialize_cache():

    os.makedirs("data", exist_ok=True)

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS response_cache (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            cache_key TEXT UNIQUE,

            question TEXT,

            response TEXT,

            input_tokens INTEGER DEFAULT 0,

            output_tokens INTEGER DEFAULT 0,

            created_at TEXT

        )
    """)

    connection.commit()

    connection.close()


# GENERATE UNIQUE REQUEST FINGERPRINT
def generate_cache_key(question, history, system_prompt, model):

    cache_data = {
        "question": question.strip().lower(),
        "history": history,
        "system_prompt": system_prompt,
        "model": model
    }

    encoded_data = json.dumps(
        cache_data,
        sort_keys=True,
        ensure_ascii=False
    )

    return hashlib.sha256(
        encoded_data.encode("utf-8")
    ).hexdigest()


# CHECK WHETHER RESPONSE EXISTS
def get_cached_response(cache_key, expiry_days=30):

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT response, created_at
        FROM response_cache
        WHERE cache_key = ?
    """, (cache_key,))

    result = cursor.fetchone()

    connection.close()

    if result is None:
        return None

    response, created_at = result

    created_date = datetime.fromisoformat(created_at)

    if datetime.now() - created_date > timedelta(days=expiry_days):
        return None

    return json.loads(response)


# SAVE NEW RESPONSE
def save_cached_response(
    cache_key,
    question,
    response,
    input_tokens=0,
    output_tokens=0
):

    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO response_cache
        (
            cache_key,
            question,
            response,
            input_tokens,
            output_tokens,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        cache_key,
        question,
        json.dumps(response, ensure_ascii=False),
        input_tokens,
        output_tokens,
        datetime.now().isoformat()
    ))

    connection.commit()

    connection.close()
