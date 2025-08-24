# Parses natural queries into simple data insight charts
def generate_chart(query):
    if "component" in query.lower():
        return "bar chart of component complexity"
    return "table of recent tickets"
