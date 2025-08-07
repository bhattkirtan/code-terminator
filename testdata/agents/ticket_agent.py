# Categorize, resolve, escalate support tickets
def classify_ticket(text):
    if "cors" in text.lower():
        return {"category": "bug", "severity": "medium", "component": "auth"}
    return {"category": "feature", "severity": "low", "component": "ui"}

def resolve_l1(ticket):
    if ticket["category"] == "bug" and ticket["component"] == "auth":
        return "Suggested CORS fix: Add allowedOrigins in backend config"
    return "Escalate to L2"

def escalate_to_l2(ticket):
    return f"Create dev story: Fix {ticket['component']} - {ticket['category']}"
