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
GITHUB_FILE_PATH = os.path.abspath(os.path.join("stats", "github.json"))
GITHUB_ACCEPTABLE_HEADERS = {
    "Accept-Encoding": "gzip, deflate, br",
    "Authorization": f"Bearer {AUTH_TOKEN}",
}

# Fetching followers number from Github API
profile_response = requests.get(f"https://api.github.com/users/{USERNAME}")

if profile_response.status_code != 200:
    err_message = profile_response.json().get("message")
    logger.error(f"Failed to fetch user information from Github API: '{err_message}'.")
    sys.exit(1)

followers = profile_response.json().get("followers")

if followers is None:
    logger.error(f"Received an empty value for user followers number.")
    sys.exit(1)

# Fetching repositories information from Github API
rep_response = requests.get(f"https://api.github.com/users/{USERNAME}/repos")

if rep_response.status_code != 200:
    err_message = rep_response.json().get("message")
    logger.error(
        f"Failed to get repositories information from Github API: '{err_message}'."
    )
    sys.exit(1)

rep_stats = rep_response.json()
rep_forks_all = sum([stat.get("forks_count") for stat in rep_stats])
rep_stargazers_all = sum([stat.get("stargazers_count") for stat in rep_stats])

# Recording statistics from Github API in file
user_info = {
    "followers": followers,
    "repo": {"total_forks": rep_forks_all, "total_stargazers": rep_stargazers_all},
}

logger.info(f"Overwriting Github API statistics in file: {GITHUB_FILE_PATH}.")

with open(GITHUB_FILE_PATH, "w") as file:
    json.dump(user_info, file)
