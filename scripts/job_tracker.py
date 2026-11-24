#!/usr/bin/env python3
"""Zero-dependency LinkedIn job deduplication tracker for Meta Muse."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_STATE_FILE = SKILL_DIR / "state" / "seen_jobs.json"
WIB = timezone(timedelta(hours=7))

JOB_ID_PATTERNS = [
    re.compile(r"/jobs/view/(?:[^/?#]*-)?(\d{6,})(?:[/?#]|$)"),
    re.compile(r"/jobs/collections/[^/?#]+/(\d{6,})(?:[/?#]|$)"),
]

KEEP_QUERY_PARAMS = {
    "id",
    "jobid",
    "job_id",
    "gh_jid",
    "requisitionid",
    "reqid",
    "postingid",
    "vacancyid",
    "jid",
}


def now_iso() -> str:
    return datetime.now(WIB).isoformat(timespec="seconds")


def extract_job_key(url: str) -> tuple[str, str]:
    """Return (dedup_key, canonical_url) for LinkedIn or non-LinkedIn job URLs."""
    raw = (url or "").strip()
    if not raw:
        return "", ""

    parsed = urlparse(raw)
    host = parsed.netloc.lower()
    query = parse_qs(parsed.query)

    # LinkedIn-specific canonicalization
    if "linkedin.com" in host:
        for param in ("currentJobId", "jobId"):
            if param in query and query[param]:
                digits = re.sub(r"\D", "", query[param][0])
                if len(digits) >= 6:
                    return f"li:{digits}", f"https://www.linkedin.com/jobs/view/{digits}/"

        for pattern in JOB_ID_PATTERNS:
            match = pattern.search(parsed.path)
            if match:
                job_id = match.group(1)
                return f"li:{job_id}", f"https://www.linkedin.com/jobs/view/{job_id}/"

    # Multi-source fallback: normalize host/path and keep only meaningful job-ID query params
    clean_path = parsed.path.rstrip("/")
    kept_params = []
    for k in sorted(query.keys()):
        if k.lower() in KEEP_QUERY_PARAMS and query[k]:
            kept_params.append((k.lower(), query[k][0].strip()))

    scheme = parsed.scheme or "https"
    normalized = f"{scheme}://{host}{clean_path}"
    if kept_params:
        normalized = f"{normalized}?{urlencode(kept_params)}"
    return f"url:{normalized}", normalized


def load_state(state_path: Path) -> dict:
    if not state_path.exists():
        return {"last_checked": None, "jobs": {}}
    try:
        with state_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "jobs" not in data:
            return {"last_checked": None, "jobs": {}}
        return data
    except (json.JSONDecodeError, OSError):
        return {"last_checked": None, "jobs": {}}


def save_state(state_path: Path, state: dict) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with state_path.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def cmd_filter(args: argparse.Namespace) -> int:
    state_path = Path(args.state)
    state = load_state(state_path)
    seen = state["jobs"]

    if args.input:
        raw_text = Path(args.input).read_text(encoding="utf-8")
    else:
        raw_text = sys.stdin.read()

    if not raw_text.strip():
        print(json.dumps({"new_count": 0, "skipped_count": 0, "new_jobs": []}, indent=2))
        return 0

    try:
        candidates = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON input: {exc}", file=sys.stderr)
        return 1

    if not isinstance(candidates, list):
        print("Error: JSON input must be a list of job objects.", file=sys.stderr)
        return 1

    timestamp = now_iso()
    new_jobs = []
    skipped_count = 0
    batch_keys = set()

    for item in candidates:
        if not isinstance(item, dict):
            continue
        url = str(item.get("url", "")).strip()
        key, canonical_url = extract_job_key(url)
        if not key:
            continue

        if key in seen or key in batch_keys:
            skipped_count += 1
            continue

        batch_keys.add(key)
        enriched = dict(item)
        enriched["job_key"] = key
        enriched["canonical_url"] = canonical_url
        new_jobs.append(enriched)

        if args.mark_seen:
            seen[key] = {
                "title": str(item.get("title", "")).strip(),
                "company": str(item.get("company", "")).strip(),
                "location": str(item.get("location", "")).strip(),
                "type": str(item.get("type", "")).strip(),
                "source": str(item.get("source", "")).strip(),
                "url": canonical_url,
                "first_seen": timestamp,
            }

    if args.mark_seen:
        state["last_checked"] = timestamp
        save_state(state_path, state)

    result = {
        "checked_at": timestamp,
        "new_count": len(new_jobs),
        "skipped_count": skipped_count,
        "total_tracked": len(seen),
        "new_jobs": new_jobs,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    state_path = Path(args.state)
    state = load_state(state_path)
    jobs = state.get("jobs", {})
    recent = sorted(
        jobs.values(),
        key=lambda j: j.get("first_seen", ""),
        reverse=True,
    )[:5]
    out = {
        "state_file": str(state_path),
        "last_checked": state.get("last_checked"),
        "total_tracked": len(jobs),
        "recent_jobs": recent,
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


def cmd_prune(args: argparse.Namespace) -> int:
    state_path = Path(args.state)
    state = load_state(state_path)
    jobs = state.get("jobs", {})

    if args.all:
        removed = len(jobs)
        state["jobs"] = {}
        save_state(state_path, state)
        print(json.dumps({"removed": removed, "remaining": 0}, indent=2))
        return 0

    cutoff = datetime.now(WIB) - timedelta(days=args.days)
    kept = {}
    removed = 0
    for key, info in jobs.items():
        first_seen = info.get("first_seen", "")
        try:
            dt = datetime.fromisoformat(first_seen)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=WIB)
            if dt >= cutoff:
                kept[key] = info
            else:
                removed += 1
        except ValueError:
            kept[key] = info

    state["jobs"] = kept
    save_state(state_path, state)
    print(json.dumps({"removed": removed, "remaining": len(kept)}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LinkedIn Intern Job Radar deduplication tracker")
    parser.add_argument(
        "--state",
        default=str(DEFAULT_STATE_FILE),
        help="Path to seen_jobs.json state file",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_filter = sub.add_parser("filter", help="Filter out already-seen jobs from JSON input")
    p_filter.add_argument("--input", help="Optional path to input JSON file (defaults to stdin)")
    p_filter.add_argument(
        "--mark-seen",
        action="store_true",
        help="Persist newly discovered jobs into state/seen_jobs.json",
    )
    p_filter.set_defaults(func=cmd_filter)

    p_status = sub.add_parser("status", help="Show tracker statistics")
    p_status.set_defaults(func=cmd_status)

    p_prune = sub.add_parser("prune", help="Remove old entries from seen_jobs.json")
    p_prune.add_argument("--days", type=int, default=60, help="Remove entries older than N days")
    p_prune.add_argument("--all", action="store_true", help="Clear all tracked jobs")
    p_prune.set_defaults(func=cmd_prune)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())