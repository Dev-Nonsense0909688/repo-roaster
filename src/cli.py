import argparse
import os
import sys
import uuid
from src.report import *
from src.github import *
PATH = "src/output/"


def parse_repo(repo: str) -> tuple[str, str]:
    if "/" not in repo:
        print("Invalid repo format. Use: user/repo")
        sys.exit(1)

    return repo.split("/", 1)


def cli():
    parser = argparse.ArgumentParser(
        prog="repo-roaster",
        description="Brutally honest GitHub repo analyzer"
    )

    parser.add_argument(
        "repo",
        help="GitHub repository in the format user/repo"
    )

    parser.add_argument(
        "-t", "--token",
        help="GitHub personal access token (or set GITHUB_TOKEN env var)",
        default=None
    )

    parser.add_argument(
        "-o", "--output",
        help="Report output file",
        default=None
    )

    args = parser.parse_args()

    token = args.token or os.getenv("GITHUB_TOKEN")
    if not token:
        print("GitHub token missing.")
        print("   Use --token or set GITHUB_TOKEN environment variable.")
        sys.exit(1)

    output = args.output or PATH+f"{uuid.uuid4()}.txt"
    os.makedirs(os.path.dirname(output), exist_ok=True)

    user, repo = parse_repo(args.repo)
    try:
        report = generate_report(token, user, repo)
        with open(output, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report saved to: {output}")

    except GitHubAuthError as e:
        print(f"Auth error: {e}")
    except GitHubRateLimitError as e:
        print(f"Rate limit: {e}")
    except GitHubNotFoundError as e:
        print(f"Not found: {e}")
    except GitHubAPIError as e:
        print(f"GitHub API error: {e}")

if __name__ == "__main__":
    cli()