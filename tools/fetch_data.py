"""Fetch every number the profile SVGs need. Standard library only, no token.

Sources
  * https://github.com/users/<user>/contributions  -- the same public HTML the
    contribution graph on your profile is rendered from.
  * the public REST API for repository + language bytes. A token is optional
    (CI passes GITHUB_TOKEN just to lift the 60 req/h anonymous rate limit).

Writes data/contributions.json and data/languages.json.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

USER = os.environ.get("PROFILE_USER", "JuanMa0912")
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
UA = "Mozilla/5.0 (compatible; profile-readme-builder/1.0)"
TIMEOUT = 30


def get(url: str, accept: str = "text/html") -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    token = os.environ.get("GITHUB_TOKEN", "")
    if token and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read().decode("utf-8", "replace")


def api(path: str):
    return json.loads(get(f"https://api.github.com{path}", "application/vnd.github+json"))


# --------------------------------------------------------------------------- #
# contributions
# --------------------------------------------------------------------------- #

TD_RE = re.compile(r"<td\b[^>]*>", re.I)
ATTR_RE = re.compile(r'([\w-]+)="([^"]*)"')
TOOLTIP_RE = re.compile(r"<tool-tip\b([^>]*)>(.*?)</tool-tip>", re.I | re.S)
COUNT_RE = re.compile(r"^\s*(No|\d[\d,]*)\s+contribution", re.I)


def fetch_contributions(user: str) -> dict:
    html = get(f"https://github.com/users/{user}/contributions")

    # id -> count, from the tool-tip elements ("12 contributions on ...").
    counts_by_id: dict[str, int] = {}
    for attrs, text in TOOLTIP_RE.findall(html):
        target = dict(ATTR_RE.findall(attrs)).get("for")
        if not target:
            continue
        match = COUNT_RE.match(re.sub(r"<[^>]+>", "", text).strip())
        if match:
            raw = match.group(1)
            counts_by_id[target] = 0 if raw.lower() == "no" else int(raw.replace(",", ""))

    days: dict[str, dict] = {}
    for tag in TD_RE.findall(html):
        attrs = dict(ATTR_RE.findall(tag))
        day = attrs.get("data-date")
        if not day:
            continue
        count = attrs.get("data-count")
        count = int(count) if count and count.isdigit() else counts_by_id.get(attrs.get("id", ""), 0)
        days[day] = {"level": int(attrs.get("data-level", 0) or 0), "count": count}

    if not days:
        raise SystemExit("could not parse any contribution days -- GitHub markup changed?")
    return days


def streaks(days: dict[str, dict]) -> dict:
    ordered = sorted(days)
    today = date.today()
    total = sum(d["count"] for d in days.values())

    longest = run = 0
    for key in ordered:
        run = run + 1 if days[key]["count"] > 0 else 0
        longest = max(longest, run)

    # Today still being empty does not break a streak -- the day is not over.
    current = 0
    cursor = today
    if days.get(cursor.isoformat(), {}).get("count", 0) == 0:
        cursor -= timedelta(days=1)
    while days.get(cursor.isoformat(), {}).get("count", 0) > 0:
        current += 1
        cursor -= timedelta(days=1)

    busiest = max(ordered, key=lambda k: days[k]["count"])
    active = sum(1 for d in days.values() if d["count"] > 0)
    return {
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "active_days": active,
        "busiest_day": {"date": busiest, "count": days[busiest]["count"]},
        "first_day": ordered[0],
        "last_day": ordered[-1],
    }


# --------------------------------------------------------------------------- #
# languages
# --------------------------------------------------------------------------- #

# Bytes-per-language over-weights anything verbose; these are the usual suspects
# for vendored or generated content and are simply not part of the story.
SKIP_LANGS = {"HTML", "CSS", "SCSS", "Makefile", "Dockerfile", "Batchfile", "Roff"}


def fetch_languages(user: str) -> dict:
    repos = []
    page = 1
    while True:
        chunk = api(f"/users/{user}/repos?per_page=100&page={page}&type=owner&sort=pushed")
        repos.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1

    totals: dict[str, int] = {}
    per_repo: dict[str, float] = {}
    repo_count: dict[str, int] = {}
    counted = 0

    for repo in repos:
        if repo.get("fork") or repo.get("archived"):
            continue
        try:
            langs = api(f"/repos/{user}/{repo['name']}/languages")
        except urllib.error.HTTPError as exc:  # private/renamed mid-run
            print(f"  ! skipped {repo['name']}: {exc}", file=sys.stderr)
            continue
        langs = {k: v for k, v in langs.items() if k not in SKIP_LANGS}
        if not langs:
            continue
        counted += 1
        repo_total = sum(langs.values()) or 1
        for name, size in langs.items():
            totals[name] = totals.get(name, 0) + size
            # Per-repo normalisation: every repo contributes exactly 1.0, split
            # by its own byte mix. Without it a single notebook repo owns the
            # chart -- .ipynb files carry their rendered outputs as source.
            per_repo[name] = per_repo.get(name, 0.0) + size / repo_total
            repo_count[name] = repo_count.get(name, 0) + 1

    grand_bytes = sum(totals.values()) or 1
    grand_repo = sum(per_repo.values()) or 1.0
    ranked = sorted(per_repo.items(), key=lambda kv: -kv[1])
    public = [r for r in repos if not r.get("fork")]
    return {
        "languages": [
            {
                "name": name,
                "share": weight / grand_repo,
                "byte_share": totals.get(name, 0) / grand_bytes,
                "bytes": totals.get(name, 0),
                "repos": repo_count.get(name, 0),
            }
            for name, weight in ranked
        ],
        "weighting": "per-repo normalised (each repo counts once, split by its byte mix)",
        "repos": len(public),
        "repos_with_code": counted,
        "stars": sum(r.get("stargazers_count", 0) for r in public),
    }


def main() -> None:
    DATA.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    print("fetching contributions ...")
    days = fetch_contributions(USER)
    payload = {"user": USER, "generated": stamp, "days": days, "stats": streaks(days)}
    (DATA / "contributions.json").write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"  {len(days)} days, {payload['stats']['total']} contributions")

    print("fetching languages ...")
    langs = fetch_languages(USER)
    langs["generated"] = stamp
    (DATA / "languages.json").write_text(json.dumps(langs, indent=1), encoding="utf-8")
    print(f"  {len(langs['languages'])} languages over {langs['repos']} repos")


if __name__ == "__main__":
    main()
