# web_app.py
import json
from ai.groq_client import ask_ai, generate_summary
from memory.conversation import create_conversation, add_user_message, add_ai_message
from memory.session_manager import save_session
from flask import Flask, render_template, request, redirect, url_for, flash
from clients.client_manager import (
    create_client,
    list_clients,
    get_client,
    update_client
)

app = Flask(__name__)
app.secret_key = "mymfit-dev-secret"  # Needed for flash messages

# ---------- Home / Client List ----------
@app.route("/")
def index():
    clients = list_clients()
    return render_template("index.html", clients=clients)

# ---------- Onboarding (Create Client) ----------
@app.route("/onboard", methods=["GET", "POST"])
def onboard():
    if request.method == "POST":
        # Collect form data
        name = request.form.get("name", "").strip()
        age = request.form.get("age", type=int)
        fitness_level = request.form.get("fitness_level", "Beginner")
        goals = request.form.get("primary_goals", "")
        equipment = request.form.get("equipment", "")
        preferred_style = request.form.get("preferred_style", "")
        time_available = request.form.get("time_available", "")
        dietary_notes = request.form.get("dietary_notes", "")
        limitations = request.form.get("limitations", "")

        if not name:
            flash("Name is required.", "error")
            return redirect(url_for("onboard"))

        # Convert comma-separated strings to lists
        primary_goals = [g.strip() for g in goals.split(",") if g.strip()]
        equipment_list = [e.strip() for e in equipment.split(",") if e.strip()]

        client = create_client(
            name=name,
            age=age,
            fitness_level=fitness_level,
            primary_goals=primary_goals,
            equipment=equipment_list,
            preferred_style=preferred_style,
            time_available=time_available,
            dietary_notes=dietary_notes,
            limitations=limitations
        )

        if client:
            flash(f"Client '{client['name']}' created successfully!", "success")
            return redirect(url_for("index"))
        else:
            flash("Failed to create client. Check the logs.", "error")

    return render_template("onboard.html")

# ---------- View Client Profile ----------
@app.route("/client/<client_id>")
def view_client(client_id):
    client = get_client(client_id)
    if not client:
        flash("Client not found.", "error")
        return redirect(url_for("index"))
    return render_template("profile.html", client=client, edit=False)

# ---------- Edit Client Profile ----------
@app.route("/client/<client_id>/edit", methods=["GET", "POST"])
def edit_client(client_id):
    client = get_client(client_id)
    if not client:
        flash("Client not found.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        updates = {
            "name": request.form.get("name", "").strip(),
            "age": request.form.get("age", type=int),
            "fitness_level": request.form.get("fitness_level"),
            "primary_goals": [g.strip() for g in request.form.get("primary_goals", "").split(",") if g.strip()],
            "equipment": [e.strip() for e in request.form.get("equipment", "").split(",") if e.strip()],
            "preferred_style": request.form.get("preferred_style", ""),
            "time_available": request.form.get("time_available", ""),
            "dietary_notes": request.form.get("dietary_notes", ""),
            "limitations": request.form.get("limitations", ""),
        }
        updated = update_client(client_id, updates)
        if updated:
            flash("Profile updated!", "success")
            return redirect(url_for("view_client", client_id=client_id))
        else:
            flash("Update failed.", "error")

    return render_template("profile.html", client=client, edit=True)
# Temporary storage for chat histories while the web server is running
chat_histories = {}


@app.route("/client/<client_id>/chat", methods=["GET", "POST"])
def chat(client_id):
    client = get_client(client_id)
    if not client:
        flash("Client not found.", "error")
        return redirect(url_for("index"))

    if client_id not in chat_histories:
        chat_histories[client_id] = create_conversation()

    history = chat_histories[client_id]

    if request.method == "POST":
        user_message = request.form.get("message", "").strip()
        
        if user_message:
            add_user_message(history, user_message)
            response_data, raw_answer = ask_ai(history)
            
            if "error" in response_data:
                flash(f"AI Error: {response_data['error']}", "error")
                history.pop()
            else:
                add_ai_message(history, raw_answer)

    # --- NEW: Format the history for the template ---
    formatted_history = []
    for msg in history:
        if msg["role"] in ["assistant", "ai"]:
            try:
                # Try to parse the JSON string into a Python dict
                parsed_content = json.loads(msg["content"])
                formatted_history.append({
                    "role": "ai",
                    "is_json": True,
                    "data": parsed_content
                })
            except json.JSONDecodeError:
                # Fallback if it's just plain text
                formatted_history.append({
                    "role": "ai",
                    "is_json": False,
                    "content": msg["content"]
                })
        else:
            formatted_history.append({
                "role": "user",
                "is_json": False,
                "content": msg["content"]
            })

    return render_template("chat.html", client=client, history=formatted_history)
    

@app.route("/client/<client_id>/save_session")
def save_and_end_session(client_id):
    if client_id in chat_histories and chat_histories[client_id]:
        history = chat_histories[client_id]
        flash("Generating summary and saving...", "success")
        summary = generate_summary(history)
        filepath = save_session(history, summary)
        
        # Clear the active chat memory
        del chat_histories[client_id]
        
        if filepath:
            flash("Session saved successfully!", "success")
        else:
            flash("Failed to save session.", "error")
    else:
        flash("No conversation to save.", "error")
        
    return redirect(url_for("view_client", client_id=client_id))
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
