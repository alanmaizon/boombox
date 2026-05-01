import os

# Map standard API_KEY to GEMINI_API_KEY for the google-adk agents
if "API_KEY" in os.environ and "GEMINI_API_KEY" not in os.environ:
    os.environ["GEMINI_API_KEY"] = os.environ["API_KEY"]
