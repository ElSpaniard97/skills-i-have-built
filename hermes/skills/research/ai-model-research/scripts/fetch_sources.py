#!/usr/bin/env python3
"""Fetch candidate AI model research items from configured feeds."""

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCES_PATH = ROOT + "/references/sources.yaml"
UA = "Hermes ai-model-research/1.0 (+https://github.com/)"


def log(message):
    print(message, file=sys.stderr)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--lookback-days", type=int, default=7)
    parser.add_argument("--sources", default=SOURCES_PATH)
    return parser.parse_args()


def load_sources(path):
    sections = {}
    current = None
    item = None
    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            section = re.match(r"^([A-Za-z0-9_]+):\s*$", line)
            if section:
                current = section.group(1)
                sections[current] = []
                item = None
                continue
            if current is None:
                continue
            entry = re.match(r"^\s*-\s+([A-Za-z0-9_]+):\s*(.*?)\s*(?:#.*)?$", line)
            if entry:
                item = {entry.group(1): parse_value(entry.group(2))}
                sections[current].append(item)
                continue
            field = re.match(r"^\s+([A-Za-z0-9_]+):\s*(.*?)\s*(?:#.*)?$", line)
            if field and item is not None:
                item[field.group(1)] = parse_value(field.group(2))
    return sections


def parse_value(value):
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [part.strip().strip("'\"") for part in inner.split(",")]
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def fetch_url(url, extra_headers=None):
    headers = {"User-Agent": UA}
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as response:
        return response.read()


def strip_html(value):
    if not value:
        return ""
    value = re.sub(r"(?is)<(script|style).*?</\1>", " ", value)
    value = re.sub(r"(?s)<[^>]+>", " ", value)
    value = (value.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
             .replace("&quot;", '"').replace("&#39;", "'"))
    return re.sub(r"\s+", " ", value).strip()


def text(node, paths):
    for path in paths:
        found = node.find(path, NS)
        if found is not None and found.text:
            return found.text.strip()
    return ""


def link_from(node):
    link = node.find("atom:link", NS)
    if link is not None and link.get("href"):
        return link.get("href").strip()
    link = node.find("link")
    if link is not None and link.text:
        return link.text.strip()
    for link in node.findall("atom:link", NS):
        if link.get("rel") in (None, "alternate") and link.get("href"):
            return link.get("href").strip()
    return ""


def parse_date(value):
    if not value:
        return None
    value = value.strip()
    value = re.sub(r"\.\d+", "", value)
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            parsed = dt.datetime.strptime(value, fmt)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=dt.timezone.utc)
            return parsed.astimezone(dt.timezone.utc)
        except ValueError:
            pass
    try:
        parsed = dt.datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return parsed.astimezone(dt.timezone.utc)
    except ValueError:
        return None


def iso_date(value):
    parsed = parse_date(value)
    return parsed.isoformat().replace("+00:00", "Z") if parsed else ""


def iso_from_unix(ts):
    return dt.datetime.fromtimestamp(float(ts), dt.timezone.utc).isoformat().replace("+00:00", "Z")


def within_lookback(value, cutoff):
    parsed = parse_date(value)
    return parsed is None or parsed >= cutoff


NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
    "media": "http://search.yahoo.com/mrss/",
    "arxiv": "http://arxiv.org/schemas/atom",
    "content": "http://purl.org/rss/1.0/modules/content/",
    "dc": "http://purl.org/dc/elements/1.1/",
}


def parse_feed(xml_bytes, source_name, kind, cutoff):
    root = ET.fromstring(xml_bytes)
    items = []
    if root.tag.endswith("rss") or root.find("channel") is not None:
        nodes = root.findall("./channel/item")
        for node in nodes:
            published = text(node, ["pubDate", "dc:date"])
            if not within_lookback(published, cutoff):
                continue
            title = text(node, ["title"])
            url = link_from(node)
            summary = strip_html(text(node, ["description", "content:encoded"]))
            items.append(make_item(source_name, title, url, published, summary, kind))
        return items

    nodes = root.findall("atom:entry", NS)
    for node in nodes:
        published = text(node, ["atom:published", "atom:updated"])
        if not within_lookback(published, cutoff):
            continue
        title = text(node, ["atom:title"])
        url = link_from(node)
        summary = strip_html(text(node, ["atom:summary", "atom:content", "media:description"]))
        items.append(make_item(source_name, title, url, published, summary, kind))
    return items


def make_item(source, title, url, published, summary, kind):
    return {
        "source": source or "",
        "title": strip_html(title),
        "url": url or "",
        "published": iso_date(published),
        "summary": summary or "",
        "kind": kind,
    }


def fetch_section(entries, kind, cutoff):
    output = []
    for entry in entries:
        name = entry.get("name", entry.get("url", "unknown"))
        url = entry.get("url", "")
        if not url:
            continue
        try:
            output.extend(parse_feed(fetch_url(url), name, kind, cutoff))
        except Exception as exc:
            log("source failed: %s <%s>: %s" % (name, url, exc))
    return output


def fetch_hn(entries, cutoff):
    output = []
    for entry in entries:
        name = entry.get("name", "HN")
        url = entry.get("url", "")
        if not url:
            continue
        try:
            data = json.loads(fetch_url(url).decode("utf-8", "replace"))
            for hit in data.get("hits", []):
                created = hit.get("created_at", "")
                if not within_lookback(created, cutoff):
                    continue
                link = hit.get("url") or ("https://news.ycombinator.com/item?id=" + str(hit.get("objectID", "")))
                title = hit.get("title") or hit.get("story_title") or ""
                points = hit.get("points") or 0
                ncomm = hit.get("num_comments") or 0
                summary = "HN: %s points, %s comments" % (points, ncomm)
                output.append(make_item(name, title, link, created, summary, "blog"))
        except Exception as exc:
            log("hn failed: %s <%s>: %s" % (name, url, exc))
    return output


def fetch_reddit(entries, cutoff):
    output = []
    headers = {"User-Agent": "Hermes ai-model-research/1.0"}
    for entry in entries:
        name = entry.get("name", entry.get("url", "Reddit"))
        url = entry.get("url", "")
        if not url:
            continue
        try:
            data = json.loads(fetch_url(url, headers).decode("utf-8", "replace"))
            for child in data.get("data", {}).get("children", []):
                post = child.get("data", {})
                if post.get("stickied") or post.get("over_18"):
                    continue
                score = int(post.get("score") or 0)
                created_utc = post.get("created_utc")
                if score < 50 or created_utc is None:
                    continue
                published_dt = dt.datetime.fromtimestamp(float(created_utc), dt.timezone.utc)
                if published_dt < cutoff:
                    continue
                permalink = post.get("permalink") or ""
                selftext = post.get("selftext") or ""
                output.append({
                    "source": name,
                    "title": strip_html(post.get("title") or ""),
                    "url": "https://reddit.com" + permalink,
                    "published": iso_from_unix(created_utc),
                    "summary": "Reddit: %s upvotes, %s comments. %s" % (
                        score,
                        post.get("num_comments") or 0,
                        strip_html(selftext)[:200],
                    ),
                    "kind": "social",
                })
        except Exception as exc:
            log("reddit failed: %s <%s>: %s" % (name, url, exc))
    return output


def fetch_bluesky(entries, cutoff):
    output = []
    for entry in entries:
        name = entry.get("name", entry.get("url", "Bluesky"))
        url = entry.get("url", "")
        if not url:
            continue
        try:
            try:
                raw = fetch_url(url)
            except urllib.error.HTTPError as exc:
                if exc.code != 403 or "public.api.bsky.app" not in url:
                    raise
                fallback_url = url.replace("https://public.api.bsky.app/", "https://api.bsky.app/")
                raw = fetch_url(fallback_url)
            data = json.loads(raw.decode("utf-8", "replace"))
            for post in data.get("posts", []):
                record = post.get("record") or {}
                author = post.get("author") or {}
                created = record.get("createdAt", "")
                if not within_lookback(created, cutoff):
                    continue
                like_count = int(post.get("likeCount") or 0)
                repost_count = int(post.get("repostCount") or 0)
                if like_count + repost_count < 10:
                    continue
                handle = author.get("handle") or ""
                uri = post.get("uri") or ""
                rkey = uri.rstrip("/").split("/")[-1] if uri else ""
                web_url = "https://bsky.app/profile/%s/post/%s" % (
                    urllib.parse.quote(handle, safe=""),
                    urllib.parse.quote(rkey, safe=""),
                )
                text_value = strip_html(record.get("text") or "")
                output.append({
                    "source": name,
                    "title": text_value[:140],
                    "url": web_url,
                    "published": iso_date(created),
                    "summary": "Bluesky @%s: %s likes, %s reposts." % (
                        handle,
                        like_count,
                        repost_count,
                    ),
                    "kind": "social",
                })
        except Exception as exc:
            log("bluesky failed: %s <%s>: %s" % (name, url, exc))
    return output


def fetch_arxiv(entries, cutoff):
    output = []
    for entry in entries:
        name = "arXiv " + entry.get("name", "")
        url = entry.get("url", "")
        try:
            output.extend(parse_feed(fetch_url(url), name, "paper", cutoff))
        except Exception as exc:
            log("arxiv failed: %s <%s>: %s" % (name, url, exc))
    return output


def main():
    args = parse_args()
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=args.lookback_days)
    sources = load_sources(args.sources)
    items = []
    items.extend(fetch_section(sources.get("official_blogs", []), "blog", cutoff))
    items.extend(fetch_hn(sources.get("hn_searches", []), cutoff))
    items.extend(fetch_section(sources.get("community_blogs", []), "blog", cutoff))
    items.extend(fetch_reddit(sources.get("reddit_subs", []), cutoff))
    items.extend(fetch_bluesky(sources.get("bluesky_searches", []), cutoff))
    items.extend(fetch_arxiv(sources.get("arxiv_categories", []), cutoff))
    items.extend(fetch_section(sources.get("youtube_channels", []), "youtube", cutoff))
    json.dump(items, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
