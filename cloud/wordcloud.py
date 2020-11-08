import sys
from json import loads
from requests import get

AUTH_TOKEN = sys.argv[1]
PROFILE_NAME = 'antonace'
GITHUB_ACCEPTABLE_HEADERS = \
    {
        'Accept': 'application/vnd.github.mercy-preview+json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Authorization': f'Bearer {AUTH_TOKEN}'
    }


def parse_topics(repository_name: str) -> list:
    topics_response = get(f'https://api.github.com/repos/{PROFILE_NAME}/{repository_name}/topics',
                          headers=GITHUB_ACCEPTABLE_HEADERS)
    topics = loads(str(topics_response.text))
    return topics["names"]


response = get(f'https://api.github.com/users/{PROFILE_NAME}/repos', headers=GITHUB_ACCEPTABLE_HEADERS)
repositories = loads(str(response.text))
repositories_topics = [' '.join(parse_topics(repo["name"])) for repo in repositories]
joined_topics = ' '.join(repositories_topics)
