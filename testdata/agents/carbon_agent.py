# Tracks model usage and CO2 estimates
def estimate_carbon(model_name, tokens):
    base_emission = 0.000001  # kg CO2 per token (mocked)
    return f"{tokens * base_emission:.4f} kg CO2 estimated for {model_name}"
