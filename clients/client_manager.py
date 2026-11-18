# ==========================================
# MYMFIT AI - CLIENT PROFILE MANAGER
# ==========================================

import os
import json
import uuid
from datetime import datetime


# Directory for storing client profiles
CLIENTS_DIR = "data/clients"


# Ensure directory exists
os.makedirs(CLIENTS_DIR, exist_ok=True)


# ==========================================
# CREATE CLIENT
# ==========================================

def create_client(
    name: str,
    age: int | None = None,
    fitness_level: str = "Beginner",
    primary_goals: list | None = None,
    equipment: list | None = None,
    preferred_style: str = "",
    time_available: str = "",
    dietary_notes: str = "",
    limitations: str = "",
    notes: str = ""
) -> dict | None:
    """
    Creates a new client profile and saves it as JSON.
    Returns the full client dictionary or None on failure.
    """

    if not name or not name.strip():
        print("Client name is required.")
        return None

    try:
        client_id = str(uuid.uuid4())[:8]  # short unique id

        now = datetime.now().isoformat()

        client = {
            "id": client_id,
            "name": name.strip(),
            "age": age,
            "fitness_level": fitness_level,
            "primary_goals": primary_goals or [],
            "equipment": equipment or [],
            "preferred_style": preferred_style.strip(),
            "time_available": time_available.strip(),
            "dietary_notes": dietary_notes.strip(),
            "limitations": limitations.strip(),
            "notes": notes.strip(),
            "created_at": now,
            "last_active": now
        }

        filepath = os.path.join(CLIENTS_DIR, f"{client_id}.json")

        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(client, file, indent=4, ensure_ascii=False)

        return client

    except (OSError, TypeError, ValueError) as error:
        print("Could not create client:", error)
        return None


# ==========================================
# LIST ALL CLIENTS
# ==========================================

def list_clients() -> list[dict]:
    """
    Returns a list of all client profiles, sorted by last_active (newest first).
    """

    clients = []

    try:
        files = [
            f for f in os.listdir(CLIENTS_DIR)
            if f.endswith(".json")
        ]

        for filename in files:
            filepath = os.path.join(CLIENTS_DIR, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as file:
                    client = json.load(file)
                    clients.append(client)
            except (OSError, json.JSONDecodeError):
                continue

        # Sort by last_active descending
        clients.sort(
            key=lambda c: c.get("last_active", ""),
            reverse=True
        )

        return clients

    except OSError as error:
        print("Could not list clients:", error)
        return []


# ==========================================
# GET SINGLE CLIENT
# ==========================================

def get_client(client_id: str) -> dict | None:
    """
    Loads a single client by ID.
    Returns the client dict or None if not found.
    """

    filepath = os.path.join(CLIENTS_DIR, f"{client_id}.json")

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)

    except FileNotFoundError:
        return None

    except (OSError, json.JSONDecodeError) as error:
        print("Could not load client:", error)
        return None


# ==========================================
# UPDATE CLIENT
# ==========================================

def update_client(client_id: str, updates: dict) -> dict | None:
    """
    Updates an existing client with the given fields.
    Automatically refreshes last_active.
    Returns the updated client or None on failure.
    """

    client = get_client(client_id)

    if not client:
        print("Client not found.")
        return None

    try:
        # Only update allowed fields
        allowed = {
            "name", "age", "fitness_level", "primary_goals",
            "equipment", "preferred_style", "time_available",
            "dietary_notes", "limitations", "notes"
        }

        for key, value in updates.items():
            if key in allowed:
                client[key] = value

        client["last_active"] = datetime.now().isoformat()

        filepath = os.path.join(CLIENTS_DIR, f"{client_id}.json")

        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(client, file, indent=4, ensure_ascii=False)

        return client

    except (OSError, TypeError, ValueError) as error:
        print("Could not update client:", error)
        return None


# ==========================================
# DELETE CLIENT
# ==========================================

def delete_client(client_id: str) -> bool:
    """
    Deletes a client profile.
    Returns True if successful, False otherwise.
    """

    filepath = os.path.join(CLIENTS_DIR, f"{client_id}.json")

    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False

    except OSError as error:
        print("Could not delete client:", error)
        return False


# ==========================================
# PROFILE TEXT FOR AI (for later injection)
# ==========================================

def get_profile_text(client: dict) -> str:
    """
    Converts a client profile into a clean text block
    that can be injected into the system prompt.
    """

    if not client:
        return "No client profile selected."

    lines = [
        f"Client Name: {client.get('name', 'Unknown')}",
    ]

    if client.get("age"):
        lines.append(f"Age: {client['age']}")

    lines.append(f"Fitness Level: {client.get('fitness_level', 'Not specified')}")

    goals = client.get("primary_goals") or []
    if goals:
        lines.append(f"Primary Goals: {', '.join(goals)}")

    equipment = client.get("equipment") or []
    if equipment:
        lines.append(f"Available Equipment: {', '.join(equipment)}")

    if client.get("preferred_style"):
        lines.append(f"Preferred Style: {client['preferred_style']}")

    if client.get("time_available"):
        lines.append(f"Time Available: {client['time_available']}")

    if client.get("dietary_notes"):
        lines.append(f"Dietary Notes: {client['dietary_notes']}")

    if client.get("limitations"):
        lines.append(f"Limitations / Health Notes: {client['limitations']}")

    if client.get("notes"):
        lines.append(f"Additional Notes: {client['notes']}")

    return "\n".join(lines)


# ==========================================
# TOUCH LAST ACTIVE (call when chatting)
# ==========================================

def touch_client(client_id: str) -> None:
    """
    Updates the last_active timestamp of a client.
    """

    update_client(client_id, {})
