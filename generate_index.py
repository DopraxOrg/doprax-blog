import os

BLOG_DIR = "blog"

posts = sorted(os.listdir(BLOG_DIR), reverse=True)

lines = []

for post in posts:
    if post.endswith(".md"):
        name = post.replace(".md","")
        parts = name.split("-")
        date = "-".join(parts[:3])
        title = " ".join(parts[3:]).replace("-", " ").title()

        lines.append(f"- **{date}** — [{title}]({BLOG_DIR}/{post})")

blog_index = "\n".join(lines)


def update_file(file):
    with open(file) as f:
        content = f.read()

    start = "<!-- BLOG START -->"
    end = "<!-- BLOG END -->"

    new_content = content.split(start)[0] + start + "\n" + blog_index + "\n" + end

    with open(file,"w") as f:
        f.write(new_content)


update_file("README.md")
update_file("index.md")
