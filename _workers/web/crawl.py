#!/usr/bin/env python3
"""
web/crawl.py — foreman worker
Depth-limited BFS web crawler. stdlib only. Robots.txt compliant. Rate limited.

Input (argv[1] JSON, falls back to stdin for direct testing):
  {
    "url":            "https://example.com",   # required — seed URL
    "max_depth":      2,                        # default 2 — link depth from seed
    "max_pages":      50,                       # default 50 — hard cap on fetched pages
    "delay_ms":       500,                      # default 500 — ms between requests
    "timeout_s":      10,                       # default 10 — per-request timeout
    "same_origin":    true,                     # default true — stay on seed domain
    "extract":        ["title","meta","links","headings"]  # default: all four
  }

Output (stdout JSON):
  {
    "success":        true,
    "pages": [{
      "url":          "...",
      "status":       200,
      "depth":        0,
      "duration_ms":  123,
      "title":        "...",
      "meta_description": "...",
      "headings":     ["h1 text", ...],     # up to 20
      "links":        ["https://...", ...]  # absolute, deduped, up to 50
    }],
    "errors":         [{"url": "...", "status": 404, "error": "..."}],
    "robots_blocked": ["https://..."],
    "skipped":        ["https://..."],      # off-origin when same_origin=true
    "duration_ms":    1234
  }
"""

import sys
import os
import json
import time
import urllib.request
import urllib.robotparser
import urllib.error
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from collections import deque

# Self-healing protocol — retry, schema validation, structured error output
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from _lib.protocol import Schema, write_output, retry  # noqa: E402

OUTPUT_SCHEMA = Schema({
    "success":       bool,
    "pages":         list,
    "errors":        list,
    "robots_blocked": list,
    "skipped":       list,
    "duration_ms":   int,
})

MAX_BODY_BYTES = 512 * 1024  # 512KB per page — avoids huge JS bundles burning memory
USER_AGENT = "foreman-crawler/1.0 (+https://github.com/michaelvgonzaga/foreman-tools)"


class _PageParser(HTMLParser):
    def __init__(self, extract):
        super().__init__(convert_charrefs=True)
        self._ex = set(extract)
        self.title = None
        self.meta_desc = None
        self.links = []
        self.headings = []
        self._in_title = False
        self._in_h = None
        self._h_buf = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._in_title = True
        elif tag == "meta" and a.get("name", "").lower() == "description" and "meta" in self._ex:
            self.meta_desc = a.get("content", "").strip()
        elif tag == "a" and "links" in self._ex:
            href = a.get("href", "").strip()
            if href and not href.startswith(("#", "javascript:", "mailto:", "tel:")):
                self.links.append(href)
        elif tag in ("h1", "h2", "h3") and "headings" in self._ex:
            self._in_h = tag
            self._h_buf = []

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif self._in_h and tag == self._in_h:
            text = "".join(self._h_buf).strip()
            if text and len(self.headings) < 20:
                self.headings.append(text)
            self._in_h = None

    def handle_data(self, data):
        if self._in_title and "title" in self._ex and self.title is None:
            self.title = data  # first text node inside <title>
        if self._in_h:
            self._h_buf.append(data)


def _fetch(url, timeout_s):
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8"},
    )
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            ct = resp.headers.get("Content-Type", "")
            dur = int((time.monotonic() - t0) * 1000)
            if "text/html" not in ct and "application/xhtml" not in ct:
                return None, resp.status, dur, f"non-html content-type: {ct.split(';')[0]}"
            body = resp.read(MAX_BODY_BYTES).decode("utf-8", "replace")
            return body, resp.status, dur, None
    except urllib.error.HTTPError as e:
        return None, e.code, int((time.monotonic() - t0) * 1000), str(e.reason)
    except urllib.error.URLError as e:
        return None, 0, int((time.monotonic() - t0) * 1000), str(e.reason)
    except Exception as e:
        return None, 0, int((time.monotonic() - t0) * 1000), str(e)


def _same_origin(base, target):
    b, t = urlparse(base), urlparse(target)
    return b.scheme == t.scheme and b.netloc == t.netloc


def _normalize(url):
    return url.split("#")[0].rstrip("/")


def crawl(cfg):
    seed = _normalize(cfg["url"])
    max_depth = int(cfg.get("max_depth", 2))
    max_pages = int(cfg.get("max_pages", 50))
    delay_ms = int(cfg.get("delay_ms", 500))
    timeout_s = int(cfg.get("timeout_s", 10))
    same_origin = bool(cfg.get("same_origin", True))
    extract = list(cfg.get("extract", ["title", "meta", "links", "headings"]))

    # robots.txt — fetch once for the seed domain
    parsed_seed = urlparse(seed)
    robots_url = f"{parsed_seed.scheme}://{parsed_seed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
    except Exception:
        rp = None

    pages = []
    errors = []
    robots_blocked = []
    skipped = []
    visited = set()
    queued = set([seed])
    queue = deque([(seed, 0)])
    t_start = time.monotonic()

    while queue and len(pages) < max_pages:
        url, depth = queue.popleft()

        if url in visited:
            continue
        visited.add(url)

        if rp and not rp.can_fetch(USER_AGENT, url):
            robots_blocked.append(url)
            continue

        if same_origin and not _same_origin(seed, url):
            skipped.append(url)
            continue

        if pages:  # rate-limit — skip on first request
            time.sleep(delay_ms / 1000.0)

        # Self-heal: retry transient network failures up to 3× with exponential backoff
        def _fetch_this():
            b, s, d, e = _fetch(url, timeout_s)
            return (b, s, d, e), e  # (result, error)

        (body, status, dur_ms, err), attempts, _ = retry(_fetch_this, max_attempts=3, base_delay_ms=300)
        if body is None and err:
            errors.append({"url": url, "status": status, "error": err, "attempts": attempts})
            continue

        page = {"url": url, "status": status, "depth": depth, "duration_ms": dur_ms}

        if body:
            p = _PageParser(extract)
            try:
                p.feed(body)
            except Exception:
                pass

            if "title" in extract:
                page["title"] = (p.title or "").strip()
            if "meta" in extract:
                page["meta_description"] = p.meta_desc or ""
            if "headings" in extract:
                page["headings"] = p.headings
            if "links" in extract:
                abs_links = []
                seen_links = set()
                for lnk in p.links:
                    try:
                        abs_lnk = _normalize(urljoin(url, lnk))
                        if abs_lnk not in seen_links and abs_lnk.startswith(("http://", "https://")):
                            seen_links.add(abs_lnk)
                            abs_links.append(abs_lnk)
                    except Exception:
                        continue
                page["links"] = abs_links[:50]

                if depth < max_depth:
                    for lnk in abs_links:
                        if lnk not in visited and lnk not in queued:
                            queued.add(lnk)
                            queue.append((lnk, depth + 1))

        pages.append(page)

    # Confidence: ratio of pages successfully fetched vs. total attempted
    attempted = len(pages) + len(errors)
    confidence = round(len(pages) / attempted, 3) if attempted > 0 else 1.0

    return {
        "success": True,
        "pages": pages,
        "errors": errors,
        "robots_blocked": robots_blocked,
        "skipped": skipped,
        "duration_ms": int((time.monotonic() - t_start) * 1000),
        "confidence": confidence,
        "self_healed": any(e.get("attempts", 1) > 1 for e in errors),
    }


if __name__ == "__main__":
    try:
        # worker-run passes JSON as argv[1]; fall back to stdin for direct invocation
        raw = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
        cfg = json.loads(raw)
        if "url" not in cfg:
            raise ValueError("missing required field: url")
        result = crawl(cfg)
        write_output(result, OUTPUT_SCHEMA)  # validates schema before printing
    except json.JSONDecodeError as e:
        print(json.dumps({"success": False, "error": f"invalid JSON input: {e}", "self_healed": False}))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e), "self_healed": False}))
        sys.exit(1)
