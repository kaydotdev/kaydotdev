import os
import sys
import json
import logging
import requests


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="[%(asctime)s] (%(levelname)s): %(message)s",
)
logger = logging.getLogger(__name__)

USERNAME = "antonace"
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
GITHUB_FILE_PATH = os.path.join("stats", "github.json")
GITHUB_ACCEPTABLE_HEADERS = {
    "Accept-Encoding": "gzip, deflate, br",
    "Authorization": f"Bearer {AUTH_TOKEN}",
}

profile_response = requests.get(f"https://api.github.com/users/{USERNAME}")

if profile_response.status_code != 200:
    err_message = profile_response.json().get("message")
    logger.error(f"Error while calling Github user API: '{err_message}'.")
    sys.exit(1)

followers = profile_response.json().get("followers")

if followers is None:
    logger.error(f"Received an empty value for user followers number.")
    sys.exit(1)

logger.info("Profile information fetched successfully.")

user_info = {
    "followers": followers
}

logger.info(f"Overwriting Github API statistics in file: {GITHUB_FILE_PATH}.")

with open(GITHUB_FILE_PATH, "w") as file:
    json.dump(user_info, file)
