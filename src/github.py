import os
import sys
import json
import logging
import requests

from typing import Optional
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


def req_github_api(url: str, msg_prefix: Optional[str] = None) -> requests.Response:
    response = requests.get(url, headers=GITHUB_ACCEPTABLE_HEADERS)

    if response.status_code != 200:
        err = response.json().get("message")
        err_msg = f"{msg_prefix or 'Failed to fetch data from Github API'}: '{err}'."

        logger.error(err_msg)
        sys.exit(1)

    return response


# Fetching followers number from Github API
user_resp = req_github_api(
    f"https://api.github.com/users/{USERNAME}",
    msg_prefix="Failed to fetch user information from Github API",
)
followers = user_resp.json().get("followers")

# Fetching repositories information from Github API
repo_resp = req_github_api(
    f"https://api.github.com/users/{USERNAME}/repos",
    msg_prefix="Failed to get repositories statistics information from Github API",
)

repositories = repo_resp.json()
rep_public = list(filter(lambda rp: not bool(rp.get("private")), repositories))

rep_forks_all = sum(map(lambda rp: rp.get("forks_count"), rep_public))
rep_stargazers_all = sum(map(lambda rp: rp.get("stargazers_count"), rep_public))
rep_watchers_all = sum(map(lambda rp: rp.get("watchers_count"), rep_public))

# Fetching views and clones from all public repositories


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
