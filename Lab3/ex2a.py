from typing import List, Tuple
import requests

def github_superstars(organization: str, token: str) -> List[Tuple[str, int]]:
    superstars = []

    with requests.Session() as session:
        session.headers['Authorization'] = f'token {token}'

        members_url = f'https://api.github.com/orgs/{organization}/members'
        members_response = session.get(members_url)
        if members_response.status_code != 200:
            print(f"Error fetching members: {members_response.status_code} - {members_response.text}")
            return []

        members = members_response.json()

        for member in members:
            username = member['login']
            repos_url = f'https://api.github.com/users/{username}/repos'
            repos_response = session.get(repos_url)
            if repos_response.status_code != 200:
                print(f"Error fetching repos for {username}: {repos_response.status_code} - {repos_response.text}")
                continue

            repos = repos_response.json()

            if repos:
                top_repo = max(repos, key=lambda repo: repo.get('stargazers_count', 0))
                superstars.append((top_repo['name'], top_repo.get('stargazers_count', 0)))

    return sorted(superstars, key=lambda x: x[1], reverse=True)
