# Repo Roaster

Repo Roaster is a command-line tool that analyzes GitHub repositories and provides a brutally honest review of their health, structure, and maintenance quality — along with actionable suggestions to improve them.

It is designed to be fast, readable, and safe to use on both small personal projects and large public repositories.

---

## Features

- Analyzes repository activity (detects inactive or abandoned projects)
- Checks README presence and quality
- Detects missing project essentials:
  - Tests
  - License
  - .gitignore
- Identifies solo-maintained repositories
- Generates a readable text report with:
  - Issues found
  - Improvement suggestions
  - Final repository score
- Gracefully handles GitHub API limitations and rate limits
- Works on large repositories without crashing

---

## Installation

### Requirements
- Python 3.10 or newer
- A GitHub Personal Access Token (PAT)

### Clone the repository
```bash
git clone https://github.com/your-username/repo-roaster.git
cd repo-roaster
