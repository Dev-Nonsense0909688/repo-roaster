from datetime import datetime, timezone
from src.checks import *
from src.github import GithubAPI


def roaster(data) -> tuple[list[str], int]:
    issues = []

    if is_repo_dead(data["last_commit"]):
        issues.append("dead_repo")

    if readme_missing(data["readme_url"]):
        issues.append("no_readme")

    if readme_too_short(data["readme_lines"]):
        issues.append("short_readme")

    if missing_tests(data["files"]):
        issues.append("no_tests")

    if missing_license(data["files"]):
        issues.append("no_license")

    if missing_gitignore(data["files"]):
        issues.append("no_gitignore")

    if is_solo(data["contributors"]):
        issues.append("solo_dev")

    score = repo_score(len(issues))
    return issues, score


def adviser(data, readme_text: str | None) -> list[str]:
    advises = []

    if is_repo_dead(data["last_commit"]):
        advises.append("Either archive or revive the repo")

    if missing_tests(data["files"]):
        advises.append("Add at least basic tests")

    if readme_text:
        text = readme_text.lower()
        if "install" not in text:
            advises.append("Add installation section to README")
        if "usage" not in text:
            advises.append("Add usage section to README")

    return advises


def generate_report(token: str, user: str, repo: str) -> str:
    github = GithubAPI(token=token)
    data = github.pull_data(user, repo)

    issues, score = roaster(data)
    advises = adviser(data, data.get("readme_text"))

    last_commit = data.get("last_commit")
    if last_commit:
        dt = datetime.fromisoformat(last_commit.replace("Z", "+00:00"))
        months_ago = round(
            (datetime.now(timezone.utc) - dt).days / 30, 1
        )
    else:
        months_ago = "unknown"

    report = f"""
---- Repo Roaster Report ----

Repo: {data['user']}/{data['repo']}
Stars: {data['stars']}
Last Commit: {months_ago} months ago

Roasts:
"""

    if not issues:
        report += "- Shockingly clean repo. Respect 🫡\n"

    if "dead_repo" in issues:
        report += "- No commits in 6+ months (dead repo energy)\n"
    if "no_gitignore" in issues:
        report += "- No .gitignore (living dangerously)\n"
    if "no_readme" in issues:
        report += "- README missing or useless\n"
    if "short_readme" in issues:
        report += "- README exists but says nothing meaningful\n"
    if "solo_dev" in issues:
        report += "- Solo dev detected (bus factor = 1)\n"
    if "no_license" in issues:
        report += "- No LICENSE file (legal jumpscare pending)\n"
    if "no_tests" in issues:
        report += "- No tests found\n"

    if advises:
        report += "\nFix Suggestions:\n"
        for tip in advises:
            report += f"- {tip}\n"

    report += f"\nFinal Score: {score}/100"

    return report.strip()
