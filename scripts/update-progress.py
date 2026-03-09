import os
import json
import requests

repo = os.getenv("REPO")
token = os.getenv("GITHUB_TOKEN")

if not repo or not token:
    raise RuntimeError("Missing REPO or GITHUB_TOKEN environment variables.")

headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github+json"
}

done_label = "done"
all_labels = ["todo", "in-progress", "done"]

owner, repo_name = repo.split("/")

url = f"https://api.github.com/repos/{owner}/{repo_name}/issues?state=all&per_page=100"

issues = []
page = 1

while True:
    response = requests.get(f"{url}&page={page}", headers=headers, timeout=30)
    response.raise_for_status()
    batch = response.json()

    if not batch:
        break

    issues.extend(batch)
    page += 1

# keep only real issues, not pull requests
issues = [issue for issue in issues if "pull_request" not in issue]

if not issues:
    percent = 0
else:
    work_issues = [
        issue for issue in issues
        if any(label["name"] in all_labels for label in issue.get("labels", []))
    ]

    done_issues = [
        issue for issue in work_issues
        if any(label["name"] == done_label for label in issue.get("labels", []))
    ]

    percent = int((len(done_issues) / max(1, len(work_issues))) * 100) if work_issues else 0

badge = {
    "schemaVersion": 1,
    "label": "progress",
    "message": f"{percent}%",
    "color": "green" if percent >= 80 else "yellow" if percent >= 40 else "red",
    "cacheSeconds": 3600
}

with open("progress.json", "w", encoding="utf-8") as f:
    json.dump(badge, f, indent=2)

print("progress.json updated:", badge)