from flask import Flask, request, jsonify
from agents.ticket_agent import classify_ticket, resolve_l1, escalate_to_l2

app = Flask(__name__)

@app.route("/ticket", methods=["POST"])
def handle_ticket():
    data = request.json
    ticket = classify_ticket(data["text"])
    ticket["resolution"] = resolve_l1(ticket)
    if "Escalate" in ticket["resolution"]:
        ticket["dev_story"] = escalate_to_l2(ticket)
    return jsonify(ticket)

if __name__ == "__main__":
    app.run(debug=True)
