import os
import sys
import json
import logging
import requests

from datetime import datetime


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="[%(asctime)s] (%(levelname)s): %(message)s",
)
logger = logging.getLogger(__name__)

USERNAME = "antonace"
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
GITHUB_RUNNER_PATH = os.path.dirname(os.path.abspath(__file__))
GITHUB_STATISTICS_PATH = os.path.join(GITHUB_RUNNER_PATH, "stats", "github.json")
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

repositories = rep_response.json()
rep_public = list(filter(lambda rp: not bool(rp.get("private")), repositories))

rep_forks_all = sum(map(lambda rp: rp.get("forks_count"), rep_public))
rep_stargazers_all = sum(map(lambda rp: rp.get("stargazers_count"), rep_public))
rep_watchers_all = sum(map(lambda rp: rp.get("watchers_count"), rep_public))

# Recording statistics from Github API in file
user_info = {
    "updated_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "followers": followers,
    "repos": {
        "forks": rep_forks_all,
        "stargazers": rep_stargazers_all,
        "watchers": rep_watchers_all,
    },
}

logger.info(f"Overwriting Github API statistics in file: {GITHUB_STATISTICS_PATH}.")

with open(GITHUB_STATISTICS_PATH, "w") as file:
    json.dump(user_info, file)
