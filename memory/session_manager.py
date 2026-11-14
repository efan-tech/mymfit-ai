# ==========================================
# MYMFIT AI - SESSION MANAGER
# ==========================================

import os
import json

from datetime import datetime


# Directory for storing conversations
SESSION_DIR = "data/sessions"


# Ensure directory exists
os.makedirs(SESSION_DIR, exist_ok=True)


# ==========================================
# SAVE SESSION
# ==========================================

def save_session(history, summary):

    try:

        # Generate unique filename
        timestamp = datetime.now()

        filename = timestamp.strftime(
            "%Y-%m-%d_session_%H%M%S.json"
        )

        filepath = os.path.join(
            SESSION_DIR,
            filename
        )

        # Prepare session information
        session_data = {

            "session_date": timestamp.isoformat(),

            "conversation": history,

            "summary": summary

        }

        # Save as JSON
        with open(filepath, "w", encoding="utf-8") as file:

            json.dump(
                session_data,
                file,
                indent=4,
                ensure_ascii=False
            )

        return filepath

    except (OSError, TypeError, ValueError) as error:

        print("Could not save session:", error)

        return None


# ==========================================
# LIST SAVED SESSIONS
# ==========================================

def list_sessions():

    try:

        files = os.listdir(SESSION_DIR)

        sessions = [

            file for file in files
            if file.endswith(".json")

        ]

        return sorted(sessions, reverse=True)

    except OSError as error:

        print("Could not access sessions:", error)

        return []


# ==========================================
# OPEN PREVIOUS SESSION
# ==========================================

def open_session(filename):

    filepath = os.path.join(
        SESSION_DIR,
        filename
    )

    try:

        with open(filepath, "r", encoding="utf-8") as file:

            return json.load(file)

    except FileNotFoundError:

        print("Session file not found.")

        return None

    except (OSError, json.JSONDecodeError) as error:

        print("Could not open session:", error)

        return None
