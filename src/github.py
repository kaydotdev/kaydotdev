import os
import sys
import json
import logging
import requests

from typing import Optional, Tuple
from datetime import datetime


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="[%(asctime)s] (%(levelname)s): %(message)s",
)
logger = logging.getLogger(__name__)

USERNAME = os.getenv("USERNAME")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
GITHUB_RUNNER_PATH = os.path.dirname(os.path.abspath(__file__))
GITHUB_STATISTICS_PATH = os.path.join(GITHUB_RUNNER_PATH, "stats", "github.json")
GITHUB_ACCEPTABLE_HEADERS = {
    "Accept-Encoding": "gzip, deflate, br",
    "Authorization": f"Bearer {AUTH_TOKEN}",
}


def req_github_api(url: str, msg_prefix: Optional[str] = None) -> requests.Response:
    """Sends a blocking GET request to the Github API endpoint.

    Args:
        url (str): HTTPS URL to the Github API endpoint
        msg_prefix (Optional[str], optional): Custom error message, if status code is not successful (!= 200). Defaults to None.

    Returns:
        requests.Response: Response from the Github API.
    """

    response = requests.get(url, headers=GITHUB_ACCEPTABLE_HEADERS)

    if response.status_code != 200:
        err = response.json().get("message", "None")
        err_msg = f"{msg_prefix or 'Failed to fetch data from Github API'}: '{err}'."

        logger.error(err_msg)
        sys.exit(1)

    return response


def req_traffic_of_repo(repo_name: str) -> Tuple[int, int]:
    """Fetches traffic information (number of unique views and clones) for a repository by specific name.

    Args:
        repo_name (str): Github repository name.

    Returns:
        Tuple[int, int]: Number of unique repository views and clones.
    """

    views_data = req_github_api(
        f"https://api.github.com/repos/{USERNAME}/{repo_name}/traffic/views",
        msg_prefix=f"Failed to fetch views of a repository '{repo_name}' from Github API",
    ).json()

    clones_data = req_github_api(
        f"https://api.github.com/repos/{USERNAME}/{repo_name}/traffic/clones",
        msg_prefix=f"Failed to fetch clones of a repository '{repo_name}' from Github API",
    ).json()

    return views_data.get("uniques", 0), clones_data.get("uniques", 0)


# Fetching followers number from Github API
user_resp = req_github_api(
    f"https://api.github.com/users/{USERNAME}",
    msg_prefix="Failed to fetch user information from Github API",
)
followers = user_resp.json().get("followers", 0)

# Fetching repositories information from Github API
repo_resp = req_github_api(
    f"https://api.github.com/users/{USERNAME}/repos",
    msg_prefix="Failed to get repositories statistics information from Github API",
)

repositories = repo_resp.json()
rep_public = list(filter(lambda rp: not bool(rp.get("private", True)), repositories))

rep_forks_all = sum(map(lambda rp: rp.get("forks_count", 0), rep_public))
rep_stargazers_all = sum(map(lambda rp: rp.get("stargazers_count", 0), rep_public))
rep_watchers_all = sum(map(lambda rp: rp.get("watchers_count", 0), rep_public))

# Fetching views and clones from all public repositories
rep_views_all, rep_clones_all = 0, 0

for rep_name in filter(
    lambda rpn: rpn is not None, map(lambda rp: rp.get("name"), rep_public)
):
    rep_views, rep_clones = req_traffic_of_repo(rep_name)

    rep_views_all += rep_views
    rep_clones_all += rep_clones

# Recording statistics from Github API in file
user_info = {
    "updated_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "followers": followers,
    "repos": {
        "forks": rep_forks_all,
        "stargazers": rep_stargazers_all,
        "watchers": rep_watchers_all,
        "views": rep_views_all,
        "clones": rep_clones_all,
    },
}

logger.info(f"Overwriting Github API statistics in file: {GITHUB_STATISTICS_PATH}.")

with open(GITHUB_STATISTICS_PATH, "w") as file:
    json.dump(user_info, file)
