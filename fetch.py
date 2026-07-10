"""Daily DevOps news pipeline for the Doprax blogs.

Runs from the doprax-blog checkout (this repo is the single source of truth). Generates one
set of picks and writes:
  - English output into this checkout (news/, README.md, index.md, docs/data.json)
  - Russian output into the doprax-blog-ru checkout at RU_REPO_DIR (news/, README.md,
    index.md, docs/data.json)

commentary_ru is a translation/localization of commentary_en for the *same* picks (same
headlines, same links) -- both languages are generated in a single Gemini call so the two
sites never drift apart on which stories were chosen.

Manual topics: set the MANUAL_TOPICS env var (one per line, "Title | URL", URL optional) to
force-include specific topics on top of the usual RSS-curated picks -- e.g. via the
workflow_dispatch "manual_topics" input when running the workflow by hand from GitHub Actions.
Manually submitted topics are always included in the output; they don't compete for the
MAX_STORIES auto-pick budget.
"""

import json
import os
import re
import time
import urllib.parse
from datetime import date, datetime

import feedparser
import requests

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_ATTEMPTS = 4
MAX_STORIES = 8  # auto-picked stories per day, on top of any manually submitted topics
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Doprax-audience DevOps terms: self-hosting / PaaS / FinOps / self-hosted AI /
# connectivity-sovereignty -- drawn from Doprax's own content & keyword docs, not generic
# enterprise "Kubernetes/Terraform/SRE" buzzwords. Edit this list to retune the daily feed;
# it's just a Python list, no other code changes needed.
DEVOPS_TERMS = [
    "Docker",
    "self-hosting",
    "CI/CD",
    "Infrastructure as Code",
    "PaaS",
    "Nginx",
    "GitLab",
    "Nextcloud",
    "n8n",
    "Ollama",
    "self-hosted LLM",
    "FinOps",
    "cloud cost",
    "V2Ray",
    "censorship circumvention",
]


def build_rss_url():
    query = "+OR+".join(f'"{urllib.parse.quote(term)}"' for term in DEVOPS_TERMS)
    return f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"


RSS_URL = build_rss_url()

STYLE_PATH = "prompts/style.md"
RU_REPO_DIR = os.environ.get("RU_REPO_DIR", "../doprax-blog-ru")

RU_MONTHS = {
    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель", 5: "Май", 6: "Июнь",
    7: "Июль", 8: "Август", 9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь",
}

RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "stories": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "index": {
                        "type": "INTEGER",
                        "description": "index of the source headline this pick is based on",
                    },
                    "commentary_en": {"type": "STRING"},
                    "commentary_ru": {"type": "STRING"},
                },
                "required": ["index", "commentary_en", "commentary_ru"],
            },
        }
    },
    "required": ["stories"],
}


def load_style_guide():
    with open(STYLE_PATH, encoding="utf-8") as f:
        return f.read()


def fetch_headlines():
    feed = feedparser.parse(RSS_URL)
    seen = set()
    headlines = []
    for entry in feed.entries:
        title = entry.title.strip()
        link = entry.link.strip()
        if title in seen:
            continue
        seen.add(title)
        headlines.append({"title": title, "link": link})
    return headlines


def parse_manual_topics(raw):
    """Parse MANUAL_TOPICS env var: one topic per line, "Title | URL" (URL optional)."""
    topics = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        if "|" in line:
            title, link = line.split("|", 1)
            title, link = title.strip(), link.strip()
        else:
            title, link = line, ""
        topics.append({"title": title, "link": link or "https://news.google.com/"})
    return topics


def select_top_stories(headlines, day, manual_count=0):
    if not headlines:
        return []
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY environment variable is not set")

    numbered_lines = []
    for i, h in enumerate(headlines):
        tag = " [MANUAL SUBMISSION -- must be included]" if i < manual_count else ""
        numbered_lines.append(f"{i}.{tag} {h['title']}")
    numbered = "\n".join(numbered_lines)

    manual_note = ""
    if manual_count:
        manual_note = (
            f"Indices 0-{manual_count - 1} are marked [MANUAL SUBMISSION]: an editor chose "
            "these specifically. You must include every one of them in your picks and write "
            "real commentary_en/commentary_ru for each, regardless of the story-count limit "
            "below. They don't count against that limit.\n\n"
        )

    prompt = (
        f"You are curating a daily DevOps news digest for {day.isoformat()}, published on both "
        "an English site and a Russian site. Below is a numbered list of headlines; most were "
        "scraped from Google News and many are near-duplicate stories covering the same event "
        "from different outlets.\n\n"
        f"{manual_note}"
        f"From the remaining (non-manual) headlines, pick at most {MAX_STORIES} of the most "
        "significant, distinct DevOps/infrastructure stories. Merge duplicate/near-duplicate "
        "coverage of the same event into a single pick. Skip opinion pieces, listicles, and "
        "minor/low-impact items.\n\n"
        "For every pick (manual or auto), write both commentary_en and commentary_ru: 2-4 "
        "sentences of actual commentary reacting to it, not a neutral restatement of the "
        "headline. commentary_ru must cover the identical story and take as commentary_en -- "
        "translated and localized into natural, idiomatic Russian, not written as an "
        "independent take and not a word-for-word crib. Follow the voice guide in the system "
        "instruction exactly, for both languages.\n\n"
        f"Headlines:\n{numbered}\n"
    )

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
        f"?key={GEMINI_API_KEY}"
    )
    body = {
        "systemInstruction": {"parts": [{"text": load_style_guide()}]},
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": RESPONSE_SCHEMA,
        },
    }

    resp = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        resp = requests.post(url, json=body, timeout=60)
        if resp.status_code not in RETRYABLE_STATUS_CODES or attempt == MAX_ATTEMPTS:
            break
        time.sleep(2 ** attempt)  # 2s, 4s, 8s
    resp.raise_for_status()
    text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    parsed = json.loads(text)

    by_index = {}
    for item in parsed.get("stories", []):
        idx = item.get("index")
        if isinstance(idx, int) and 0 <= idx < len(headlines):
            by_index[idx] = item

    # Manual submissions are always included and don't count against MAX_STORIES; auto-picks
    # fill the remaining budget in the order Gemini returned them.
    final_indices = list(range(manual_count))
    auto_added = 0
    for item in parsed.get("stories", []):
        idx = item.get("index")
        if not isinstance(idx, int) or not (0 <= idx < len(headlines)):
            continue
        if idx < manual_count or idx in final_indices:
            continue
        if auto_added >= MAX_STORIES:
            continue
        final_indices.append(idx)
        auto_added += 1

    stories = []
    for idx in final_indices:
        item = by_index.get(idx, {})
        commentary_en = item.get("commentary_en", "").strip()
        commentary_ru = item.get("commentary_ru", "").strip()
        if idx < manual_count and not commentary_en:
            # Gemini didn't return this manual index -- surface it instead of silently
            # dropping the editor's explicit request.
            commentary_en = (
                "(Manually submitted topic; the model did not return commentary for it this "
                "run -- rerun the workflow to retry.)"
            )
            commentary_ru = (
                "(Тема добавлена вручную; модель не вернула комментарий в этом запуске — "
                "перезапустите workflow.)"
            )
        stories.append(
            {
                "title": headlines[idx]["title"],
                "link": headlines[idx]["link"],
                "commentary_en": commentary_en,
                "commentary_ru": commentary_ru,
            }
        )
    return stories


# ---------------------------------------------------------------------------
# Per-language file writers. Each is parameterized by base_dir (repo checkout root) and
# lang ("en" or "ru") so the same functions serve both doprax-blog and doprax-blog-ru.
# ---------------------------------------------------------------------------

def month_file_path(base_dir, day):
    return os.path.join(base_dir, "news", f"{day.strftime('%Y-%m')}.md")


def month_label(day_or_dt, lang):
    if lang == "ru":
        return f"{RU_MONTHS[day_or_dt.month]} {day_or_dt.year}"
    return day_or_dt.strftime("%B %Y")


def commentary_for(story, lang):
    return story["commentary_ru"] if lang == "ru" else story["commentary_en"]


def empty_day_text(lang):
    return (
        "_За этот день заметных новостей не найдено._\n\n"
        if lang == "ru"
        else "_No notable DevOps news found today._\n\n"
    )


def format_day_section(day, stories, lang):
    lines = [f"## {day.isoformat()}\n\n"]
    if stories:
        for s in stories:
            lines.append(
                f"- **{s['title']}**\n  {commentary_for(s, lang)}\n  [Read more]({s['link']})\n\n"
            )
    else:
        lines.append(empty_day_text(lang))
    return "".join(lines)


def already_ran_today(base_dir, day):
    path = month_file_path(base_dir, day)
    if not os.path.exists(path):
        return False
    with open(path, encoding="utf-8") as f:
        return f"## {day.isoformat()}" in f.read()


def replace_day_in_month_file(base_dir, day, stories, lang):
    """Write (or, on a same-day rerun -- e.g. adding manual topics later -- replace) this
    day's section in the month archive file. Never appends a duplicate section for a day
    that's already present."""
    news_dir = os.path.join(base_dir, "news")
    os.makedirs(news_dir, exist_ok=True)
    path = month_file_path(base_dir, day)
    day_header = f"## {day.isoformat()}"
    new_section = format_day_section(day, stories, lang)

    if not os.path.exists(path):
        content = f"# {month_label(day, lang)}\n\n" + new_section
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    with open(path, encoding="utf-8") as f:
        content = f.read()

    if day_header not in content:
        with open(path, "a", encoding="utf-8") as f:
            f.write(new_section)
        return path

    start = content.index(day_header)
    search_from = start + len(day_header)
    next_marker = content.find("\n## ", search_from)
    end = len(content) if next_marker == -1 else next_marker + 1
    content = content[:start] + new_section + content[end:]
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def list_month_files(base_dir):
    news_dir = os.path.join(base_dir, "news")
    if not os.path.isdir(news_dir):
        return []
    files = [f for f in os.listdir(news_dir) if re.fullmatch(r"\d{4}-\d{2}\.md", f)]
    return sorted(files, reverse=True)


def format_archive_section(base_dir, lang):
    heading = "## Архив\n\n" if lang == "ru" else "## Archive\n\n"
    lines = [heading]
    for fname in list_month_files(base_dir):
        ym = fname[:-3]
        d = datetime.strptime(ym, "%Y-%m")
        lines.append(f"- [{month_label(d, lang)}](news/{fname})\n")
    return "".join(lines) + "\n"


def upsert_news_block(content, day, stories, lang, base_dir):
    """Insert/replace a 'Daily DevOps News' block, marked with NEWS START/END, without
    touching the existing tutorial-post BLOG START/END block (generate_index.py owns that)."""
    marker_start = "<!-- NEWS START -->"
    marker_end = "<!-- NEWS END -->"

    heading = "## Ежедневные новости DevOps" if lang == "ru" else "## Daily DevOps News"
    latest_label = (
        f"### Свежее — {day.isoformat()}\n\n" if lang == "ru" else f"### Latest — {day.isoformat()}\n\n"
    )

    body = latest_label
    if stories:
        for s in stories:
            body += f"- **{s['title']}**\n  {commentary_for(s, lang)}\n  [Read more]({s['link']})\n\n"
    else:
        body += empty_day_text(lang)
    body += format_archive_section(base_dir, lang)

    if marker_start in content and marker_end in content:
        pre, rest = content.split(marker_start, 1)
        _, post = rest.split(marker_end, 1)
        return pre + marker_start + "\n" + body + marker_end + post

    section = f"{heading}\n\n{marker_start}\n{body}{marker_end}\n\n"
    anchor = "<!-- BLOG START -->"
    if anchor in content:
        # ensure a blank line separates whatever precedes the anchor from our new heading
        prefix, _, suffix = content.partition(anchor)
        prefix = prefix.rstrip("\n") + "\n\n"
        return prefix + section + anchor + suffix
    return content.rstrip("\n") + "\n\n" + section


def update_readme_and_index(base_dir, day, stories, lang):
    for filename in ("README.md", "index.md"):
        path = os.path.join(base_dir, filename)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            content = f.read()
        new_content = upsert_news_block(content, day, stories, lang, base_dir)
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)


def update_data_json(base_dir, day, stories, lang):
    data_path = os.path.join(base_dir, "docs", "data.json")
    if os.path.exists(data_path):
        with open(data_path, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"months": {}}

    month = data["months"].setdefault(day.strftime("%Y-%m"), {})
    month[day.isoformat()] = [
        {"title": s["title"], "link": s["link"], "commentary": commentary_for(s, lang)}
        for s in stories
    ]

    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def write_language(base_dir, day, stories, lang):
    if not os.path.isdir(base_dir):
        raise RuntimeError(f"target checkout not found: {base_dir}")
    replace_day_in_month_file(base_dir, day, stories, lang)
    update_readme_and_index(base_dir, day, stories, lang)
    update_data_json(base_dir, day, stories, lang)


def main():
    today = date.today()
    manual_topics = parse_manual_topics(os.environ.get("MANUAL_TOPICS", ""))

    if not manual_topics and already_ran_today(".", today):
        print(f"{today.isoformat()} already logged in EN archive, skipping run.")
        return

    headlines = fetch_headlines()
    combined_headlines = manual_topics + headlines
    stories = select_top_stories(combined_headlines, today, manual_count=len(manual_topics))

    write_language(".", today, stories, "en")
    write_language(RU_REPO_DIR, today, stories, "ru")


if __name__ == "__main__":
    main()
