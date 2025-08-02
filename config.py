# Moodle API Configuration
# Fill in your details below

# Concordia Moodle URL
MOODLE_URL = "https://moodle.concordia.ca/moodle"

# Your Moodle API token
# See docs/obtaining_api_token.md for instructions on how to get this
API_TOKEN = "YOUR_MOODLE_API_TOKEN_HERE"  # Your Moodle API token

# OpenAI API key for PDF summarization
# Get your API key from https://platform.openai.com/account/api-keys
OPENAI_API_KEY = "YOUR_OPENAI_API_KEY_HERE"  # Set this in a .env file or as an environment variable, do not commit real keys

# Default request parameters
DEFAULT_PARAMS = {
    "moodlewsrestformat": "json"  # Format for API responses
}
