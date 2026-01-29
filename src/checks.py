from datetime import datetime, timezone


def is_repo_dead(last_commit: str, days: int = 180) -> bool:
    if not last_commit:
        return True

    dt = datetime.fromisoformat(last_commit.replace("Z", "+00:00"))
    delta = (datetime.now(timezone.utc) - dt).days
    return delta > days


def readme_missing(readme_url) -> bool:
    return readme_url is None


def readme_too_short(readme_lines: int, min_lines: int = 20) -> bool:
    if readme_lines is None:
        return True
    return readme_lines < min_lines


def missing_tests(files: list[str]) -> bool:
    return not any("test" in f.lower() for f in files)


def missing_license(files: list[str]) -> bool:
    return not any("license" in f.lower() for f in files)


def missing_gitignore(files: list[str]) -> bool:
    return ".gitignore" not in [f.lower() for f in files]


def is_solo(contributors: int) -> bool:
    return contributors == 1


def repo_score(issue_count: int, max_score: int = 100) -> int:
    return max(max_score - issue_count * 10, 0)
