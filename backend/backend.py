import os
from flask import Flask, render_template, request
import database as db

app = Flask(__name__)

db.init()


@app.route("/")
def home():
    return render_template("website.html")


@app.route("/id")
def device():
    return render_template("id.html")


@app.route("/timer")
def timer():
    return render_template("timer.html")


@app.route("/set_timer", methods=["POST"])
def set_timer():

    data = request.get_json()

    bot_id = data.get("id")
    target_time = data.get("target_time")
    seconds = data.get("seconds")

    if not bot_id or seconds is None:
        print("ERROR: Missing ID or seconds")
        return "Missing ID or seconds", 400

    if not db.check_id(bot_id):
        print("ERROR: ID does not exist")
        return "ID does not exist", 400

    try:
        seconds = int(seconds)
    except ValueError:
        print("ERROR: Invalid seconds")
        return "Invalid seconds", 400

    if seconds <= 0:
        print("ERROR: Timer must be greater than 0")
        return "Timer must be greater than 0", 400

    db.set_timer(bot_id, seconds)

    return "Timer saved"

@app.route("/cancel_timer", methods=["POST"])
def cancel_timer():

    data = request.get_json()

    bot_id = data.get("id")

    if not bot_id:
        return "Missing ID", 400

    if not db.check_id(bot_id):
        return "ID does not exist", 400

    # Remove timer from database
    db.clear_timer(bot_id)

    # Tell ESP32 to stop its local timer
    db.set_command(bot_id, "cancel_timer")

    print("TIMER CANCELLED:", bot_id)

    return "Timer cancelled"

@app.route("/online", methods=["POST"])
def online():

    data = request.json

    print("Received:", data)

    bot_id = data["id"]

    if not db.check_id(bot_id):
        db.add_device(bot_id)

    print(bot_id, "is online")

    return "ok"

@app.route("/start", methods=["POST"])
def start():

    data = request.get_json()

    bot_id = data.get("id")

    if not bot_id:
        return "Missing ID", 400

    if not db.check_id(bot_id):
        return "ID does not exist", 400

    db.clear_timer(bot_id)

    db.set_command(bot_id, "press")

    print("START COFFEE:", bot_id)

    return "Coffee started"

@app.route("/request")
def request_timer():

    bot_id = request.args.get("id")

    if not bot_id:
        return "none"

    if not db.check_id(bot_id):
        return "none"

    command = db.get_command(bot_id)

    if command != "none":

        db.clear_command(bot_id)

        print("Sending command:", command)

        return command

    seconds = db.get_timer(bot_id)

    if seconds > 0:

        db.clear_timer(bot_id)

        print("Sending timer:", seconds)

        return str(seconds)

    return "none"

@app.route("/save_id", methods=["POST"])
def save_id():

    data = request.json

    bot_id = data["id"]

    if db.check_id(bot_id):

        return {
            "success": True,
            "message": "ID saved"
        }

    return {
        "success": False,
        "message": "This ID does not exist"
    }

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )

# 3FCD55319C3C