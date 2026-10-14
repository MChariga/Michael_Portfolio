"""Lists your public GitHub repos as ready-to-paste project entries.
Run: python fetch_repos.py   ->  creates repos_draft.json. Copy the repos you want into the "projects" list in content.json."""
import json, urllib.request
USER = "MChariga"
repos = json.load(urllib.request.urlopen(f"https://api.github.com/users/{USER}/repos?per_page=100&sort=updated"))
out = [{"type": "code", "title": r["name"].replace("-", " ").replace("_", " ").title(), "tags": [t for t in [r["language"]] + r.get("topics", []) if t][:4] or ["Analysis"],
        "desc": r["description"] or "ADD A ONE-LINE DESCRIPTION: the question, the data, what you found.", "link": r["html_url"], "label": "View code on GitHub"}
       for r in repos if not r["fork"]]
json.dump(out, open("repos_draft.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(len(out), "repos written to repos_draft.json")
