#!/usr/bin/env python3
"""Deduplicate candidate items against a URL-keyed state file."""

import datetime as dt
import json
import os
import re
import sys
import urllib.parse


STATE_PATH = os.path.expanduser("~/.hermes/cron/state/ai-research-seen.json")
TRACKING_PARAMS = re.compile(r"^(utm_|fbclid$|gclid$|mc_cid$|mc_eid$|_hs)", re.I)


def log(message):
    print(message, file=sys.stderr)


def load_json(path, fallback):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return fallback
    except Exception as exc:
        log("state read failed, starting fresh: %s" % exc)
        return fallback


def canonical_url(url):
    url = (url or "").strip()
    if not url:
        return ""
    parsed = urllib.parse.urlsplit(url)
    scheme = (parsed.scheme or "https").lower()
    netloc = parsed.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = re.sub(r"/+$", "", parsed.path or "/")
    query_pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query_pairs = [(k, v) for k, v in query_pairs if not TRACKING_PARAMS.search(k)]
    query = urllib.parse.urlencode(sorted(query_pairs), doseq=True)
    return urllib.parse.urlunsplit((scheme, netloc, path, query, ""))


def item_key(item):
    key = canonical_url(item.get("url", ""))
    if key:
        return key
    title = re.sub(r"\s+", " ", item.get("title", "").lower()).strip()
    return "title:%s:%s" % (item.get("source", ""), title)


def main():
    try:
        items = json.load(sys.stdin)
    except Exception as exc:
        log("input JSON parse failed: %s" % exc)
        sys.exit(1)
    if not isinstance(items, list):
        log("input must be a JSON list")
        sys.exit(1)

    state = load_json(STATE_PATH, {})
    if not isinstance(state, dict):
        state = {}

    now = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    new_items = []
    for item in items:
        if not isinstance(item, dict):
            continue
        key = item_key(item)
        if not key or key in state:
            continue
        state[key] = {
            "first_seen": now,
            "title": item.get("title", ""),
            "source": item.get("source", ""),
            "url": item.get("url", ""),
            "kind": item.get("kind", ""),
        }
        new_items.append(item)

    try:
        os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
        tmp_path = STATE_PATH + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump(state, fh, ensure_ascii=False, indent=2, sort_keys=True)
            fh.write("\n")
        os.replace(tmp_path, STATE_PATH)
    except Exception as exc:
        log("state write failed: %s" % exc)

    json.dump(new_items, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
