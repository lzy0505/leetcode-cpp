#!/usr/bin/env python3
"""Scrape LeetCode problems and create C++ solution stubs."""

import argparse
import json
import os
import re
import sys
import textwrap
import time
import urllib.request
import urllib.error
from html.parser import HTMLParser

GRAPHQL_URL = "https://leetcode.com/graphql"

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Referer": "https://leetcode.com",
}


class HTMLToText(HTMLParser):
    """Minimal HTML-to-text converter for problem descriptions."""

    def __init__(self):
        super().__init__()
        self._parts: list[str] = []
        self._in_pre = False
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag == "pre":
            self._in_pre = True
        elif tag == "p":
            self._parts.append("\n")
        elif tag == "br":
            self._parts.append("\n")
        elif tag in ("ul", "ol"):
            self._parts.append("\n")
        elif tag == "li":
            self._parts.append("  - ")
        elif tag == "sup":
            self._parts.append("^")
        elif tag in ("style", "script"):
            self._skip = True

    def handle_endtag(self, tag):
        if tag == "pre":
            self._in_pre = False
            self._parts.append("\n")
        elif tag == "li":
            self._parts.append("\n")
        elif tag in ("style", "script"):
            self._skip = False

    def handle_data(self, data):
        if self._skip:
            return
        self._parts.append(data)

    def get_text(self) -> str:
        text = "".join(self._parts)
        # collapse excessive blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()


def html_to_text(html: str) -> str:
    parser = HTMLToText()
    parser.feed(html)
    return parser.get_text()


def graphql_request(query: str, variables: dict) -> dict:
    payload = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(GRAPHQL_URL, data=payload, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def fetch_problem_list(limit: int = 0, difficulty: str = "", category: str = "") -> list[dict]:
    """Fetch problem list from LeetCode. limit=0 means all."""
    query = """
    query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
        problemsetQuestionList: questionList(
            categorySlug: $categorySlug
            limit: $limit
            skip: $skip
            filters: $filters
        ) {
            total: totalNum
            questions: data {
                frontendQuestionId: questionFrontendId
                title
                titleSlug
                difficulty
                topicTags { name }
                paidOnly: isPaidOnly
            }
        }
    }
    """
    filters = {}
    if difficulty:
        filters["difficulty"] = difficulty.upper()

    data = graphql_request(query, {
        "categorySlug": category or "all-code-essentials",
        "limit": limit if limit > 0 else 10000,
        "skip": 0,
        "filters": filters,
    })
    return data["data"]["problemsetQuestionList"]["questions"]


def fetch_problem_detail(slug: str) -> dict:
    """Fetch full problem detail including description and code snippets."""
    query = """
    query questionDetail($titleSlug: String!) {
        question(titleSlug: $titleSlug) {
            questionFrontendId
            title
            titleSlug
            difficulty
            content
            topicTags { name }
            codeSnippets { langSlug code }
            isPaidOnly
        }
    }
    """
    data = graphql_request(query, {"titleSlug": slug})
    return data["data"]["question"]


def slugify(title: str) -> str:
    s = title.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def make_dir_name(qid: str, title: str) -> str:
    num = qid.zfill(4)
    return f"{num}-{slugify(title)}"


def create_solution_file(base_dir: str, problem: dict, overwrite: bool = False):
    """Create the directory and solution.cpp for a problem."""
    qid = problem["questionFrontendId"]
    title = problem["title"]
    dirname = make_dir_name(qid, title)
    dirpath = os.path.join(base_dir, dirname)
    filepath = os.path.join(dirpath, "solution.cpp")

    if os.path.exists(filepath) and not overwrite:
        print(f"  skip {dirname} (exists)")
        return dirpath

    os.makedirs(dirpath, exist_ok=True)

    # Extract C++ code snippet
    cpp_code = ""
    for snippet in (problem.get("codeSnippets") or []):
        if snippet["langSlug"] == "cpp":
            cpp_code = snippet["code"]
            break

    # Convert HTML description to text
    description = ""
    if problem.get("content"):
        description = html_to_text(problem["content"])

    difficulty = problem.get("difficulty", "")
    tags = ", ".join(t["name"] for t in (problem.get("topicTags") or []))
    url = f"https://leetcode.com/problems/{problem['titleSlug']}/"

    lines = [
        f"// {qid}. {title}",
        f"// {url}",
        f"// Difficulty: {difficulty}",
        f"// Tags: {tags}",
        "//",
    ]

    if description:
        for line in description.splitlines():
            lines.append(f"// {line}" if line.strip() else "//")

    lines.append("")
    lines.append("#include <bits/stdc++.h>")
    lines.append("using namespace std;")
    lines.append("")

    if cpp_code:
        lines.append(cpp_code)
    else:
        lines.append("// No C++ template available (possibly premium)")

    lines.append("")

    with open(filepath, "w") as f:
        f.write("\n".join(lines))

    print(f"  created {dirname}/solution.cpp")
    return dirpath


def cmd_fetch(args):
    """Fetch specific problems by number or slug."""
    base = os.path.dirname(os.path.abspath(__file__))

    for ident in args.problems:
        print(f"Fetching {ident}...")
        # If numeric, first find the slug
        if ident.isdigit():
            problems = fetch_problem_list()
            slug = None
            for p in problems:
                if p["frontendQuestionId"] == ident:
                    slug = p["titleSlug"]
                    break
            if not slug:
                print(f"  problem #{ident} not found")
                continue
        else:
            slug = ident

        try:
            detail = fetch_problem_detail(slug)
        except urllib.error.HTTPError as e:
            print(f"  HTTP error: {e.code}")
            continue

        if detail is None:
            print(f"  not found or premium-only")
            continue

        if detail.get("isPaidOnly") and not detail.get("content"):
            print(f"  premium-only, creating stub anyway")

        create_solution_file(base, detail, overwrite=args.overwrite)
        time.sleep(0.5)  # be polite


def cmd_batch(args):
    """Fetch a batch of problems."""
    base = os.path.dirname(os.path.abspath(__file__))

    print("Fetching problem list...")
    problems = fetch_problem_list(difficulty=args.difficulty)
    free_problems = [p for p in problems if not p["paidOnly"]]
    free_problems.sort(key=lambda p: int(p["frontendQuestionId"]))

    if args.limit > 0:
        free_problems = free_problems[:args.limit]

    print(f"Found {len(free_problems)} free problems, fetching details...")

    for i, p in enumerate(free_problems):
        qid = p["frontendQuestionId"]
        dirname = make_dir_name(qid, p["title"])
        filepath = os.path.join(base, dirname, "solution.cpp")

        if os.path.exists(filepath) and not args.overwrite:
            continue

        print(f"[{i+1}/{len(free_problems)}] {qid}. {p['title']}")
        try:
            detail = fetch_problem_detail(p["titleSlug"])
            if detail:
                create_solution_file(base, detail, overwrite=args.overwrite)
        except urllib.error.HTTPError as e:
            print(f"  HTTP error: {e.code}, skipping")
        except Exception as e:
            print(f"  error: {e}, skipping")

        time.sleep(1.0)  # rate limit


def cmd_list(args):
    """List available problems."""
    problems = fetch_problem_list(difficulty=args.difficulty)
    free = [p for p in problems if not p["paidOnly"]]
    free.sort(key=lambda p: int(p["frontendQuestionId"]))

    if args.limit > 0:
        free = free[:args.limit]

    for p in free:
        tags = ", ".join(t["name"] for t in (p.get("topicTags") or []))
        diff = p["difficulty"][0]  # E/M/H
        print(f"{p['frontendQuestionId']:>4}  [{diff}]  {p['title']:50s}  {tags}")


def main():
    parser = argparse.ArgumentParser(description="LeetCode problem scraper")
    sub = parser.add_subparsers(dest="command", required=True)

    # fetch specific problems
    p_fetch = sub.add_parser("fetch", help="Fetch specific problems by number or slug")
    p_fetch.add_argument("problems", nargs="+", help="Problem numbers (e.g. 1 42) or slugs (e.g. two-sum)")
    p_fetch.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    p_fetch.set_defaults(func=cmd_fetch)

    # batch fetch
    p_batch = sub.add_parser("batch", help="Fetch many problems at once")
    p_batch.add_argument("--limit", type=int, default=50, help="Max problems to fetch (0=all)")
    p_batch.add_argument("--difficulty", choices=["easy", "medium", "hard"], default="")
    p_batch.add_argument("--overwrite", action="store_true")
    p_batch.set_defaults(func=cmd_batch)

    # list problems
    p_list = sub.add_parser("list", help="List available problems")
    p_list.add_argument("--limit", type=int, default=50)
    p_list.add_argument("--difficulty", choices=["easy", "medium", "hard"], default="")
    p_list.set_defaults(func=cmd_list)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
