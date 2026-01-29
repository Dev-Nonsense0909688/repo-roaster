import requests
import base64
from requests.exceptions import RequestException, Timeout


class GitHubAPIError(Exception):
    """Base GitHub API error"""


class GitHubAuthError(GitHubAPIError):
    pass


class GitHubRateLimitError(GitHubAPIError):
    pass


class GitHubNotFoundError(GitHubAPIError):
    pass


class GithubAPI:
    def __init__(self, token: str | None = None, timeout: int = 5):
        self.TOKEN = token
        self.timeout = timeout

    def _headers(self):
        headers = {
            "Accept": "application/vnd.github+json"
        }
        if self.TOKEN:
            headers["Authorization"] = f"Bearer {self.TOKEN}"
        return headers

    def auth(self, token: str) -> tuple[bool, str]:
        if not token:
            raise GitHubAuthError("GitHub token missing")

        try:
            res = requests.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/vnd.github+json"
                },
                timeout=self.timeout
            )
        except Timeout:
            raise GitHubAPIError("GitHub API timed out")
        except RequestException as e:
            raise GitHubAPIError(f"Network error: {e}")

        if res.status_code == 200:
            self.TOKEN = token
            return True, res.json()["login"]

        if res.status_code == 401:
            raise GitHubAuthError("Invalid GitHub token")

        if res.status_code == 403:
            raise GitHubRateLimitError("Access forbidden or rate limit exceeded")

        raise GitHubAPIError(
            f"GitHub auth failed ({res.status_code}): {res.text}"
        )

    def _get(self, url: str):
        try:
            return requests.get(
                url,
                headers=self._headers(),
                timeout=self.timeout
            )
        except Timeout:
            raise GitHubAPIError("GitHub API request timed out")
        except RequestException as e:
            raise GitHubAPIError(f"Network error: {e}")

    def pull_readme(self, base: str) -> tuple[str | None, int | None]:
        r = self._get(base + "/readme")

        if r.status_code == 404:
            return None, None

        if r.status_code != 200:
            raise GitHubAPIError(
                f"Failed to fetch README ({r.status_code})"
            )

        data = r.json()
        content = base64.b64decode(
            data.get("content", "")
        ).decode("utf-8", errors="ignore")

        return data.get("download_url"), content.count("\n")

    def pull_files(self, base: str) -> list[str]:
        r = self._get(base + "/contents")

        if r.status_code == 404:
            return []

        if r.status_code != 200:
            raise GitHubAPIError(
                f"Failed to fetch repo contents ({r.status_code})"
            )

        return [item["name"] for item in r.json()]

    def pull_contributors(self, base: str) -> int:
        r = self._get(base + "/contributors")

        if r.status_code == 404:
            return 0

        if r.status_code != 200:
            raise GitHubAPIError(
                f"Failed to fetch contributors ({r.status_code})"
            )

        return len(r.json())

    def pull_data(self, user: str, repo: str) -> dict:
        url = f"https://api.github.com/repos/{user.strip().lower()}/{repo}"
        r = self._get(url)

        if r.status_code == 404:
            raise GitHubNotFoundError(
                f"Repository '{user}/{repo}' not found"
            )

        if r.status_code == 403:
            raise GitHubRateLimitError(
                "GitHub API rate limit exceeded"
            )

        if r.status_code != 200:
            raise GitHubAPIError(
                f"Failed to fetch repo ({r.status_code})"
            )

        repo_data = r.json()
        readme_url, readme_lines = self.pull_readme(url)

        return {
            "last_commit": repo_data.get("pushed_at"),
            "readme_url": readme_url,
            "readme_lines": readme_lines,
            "files": self.pull_files(url),
            "contributors": self.pull_contributors(url),
            "stars": repo_data.get("stargazers_count", 0),
            "repo": repo,
            "user": user
        }
