from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime
import re
import os

from utils.summarize import summarize_title

LOG_DIR = "md_logs"


def sanitize_filename(title: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", title).strip().replace(" ", "_")


def save_markdown_report(data: Dict[str, Any], file_path: str = None) -> str:
    query = data.get("user_query", "").strip()
    summary_title = summarize_title(query) if query else "report"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    file_name = f"{summary_title}_{timestamp}.md"
    file_path = Path(LOG_DIR) / file_name

    file_path.parent.mkdir(parents=True, exist_ok=True)

    lines: List[str] = ["# 📘 Final Answer Report\n", "## 🧠 Original Question", query + "\n", "## ✍️ Rephrased Question",
                        data.get("rephrased_query", "").strip() + "\n", "## 📌 On Topic",
                        "✅ Yes\n" if data.get("on_topic") else "❌ No\n", "## 📚 Detected Library",
                        f"`{data.get('library', '-')}`\n", "## 📄 Scrape Status",
                        "✅ Done\n" if data.get("scrape_done") else "❌ Not done\n", "## 📥 Ingest Status",
                        "✅ Done\n" if data.get("ingest_done") else "❌ Not done\n", "## 💬 Chat History"]

    for msg in data.get("chat_history", []):
        role = msg.get("role", "unknown").capitalize()
        content = msg.get("content", "").strip()
        lines.append(f"\n**{role}:**\n{content}\n")

    lines.append("## 📑 Retrieved Documents")
    for i, doc in enumerate(data.get("retrieved_docs", []), 1):
        title = doc.page_content.strip().split('\n')[0][:80] if hasattr(doc, "page_content") else "-"
        source = doc.metadata.get("source", "unknown").split("\\")[-1] if hasattr(doc, "metadata") else "-"
        lines.append(f"{i}. **{title}**\n   - *Source:* `{source}`")

    warning = data.get("doc_link_mismatch_warning", [])
    if warning:
        lines.append("## ⚠️ Warnings")
        lines.append(f"- {warning}")
    lines.append("```python")

    file_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ Markdown report saved to: {file_path}")

    return str(file_path)


def list_markdown_titles() -> List[str]:
    if not os.path.exists(LOG_DIR):
        return []

    def extract_timestamp(file_name: str) -> str:
        match = re.search(r'_(\d{8}_\d{6})\.md$', file_name)
        return match.group(1) if match else "00000000_000000"

    markdown_files = [
        (f, extract_timestamp(f)) for f in os.listdir(LOG_DIR) if f.endswith(".md")
    ]
    sorted_files = sorted(markdown_files, key=lambda x: x[1], reverse=True)

    titles = []
    for f, _ in sorted_files:
        title_part = re.sub(r'_\d{8}_\d{6}\.md$', '', f)  # timestamp ve .md kaldır
        title = title_part.replace("_", " ").capitalize()
        titles.append(title)

    return titles


def normalize_title(title: str) -> str:
    return title.lower().replace(" ", "_").strip()


def load_markdown_content(selected_title: str) -> str:
    if not os.path.exists(LOG_DIR):
        return "⚠️ No logs found."

    normalized_selected = normalize_title(selected_title)

    for f in os.listdir(LOG_DIR):
        if f.endswith(".md"):
            base = f[:-3]
            base_no_ts = re.sub(r'_\d{8}_\d{6}$', '', base)
            if normalize_title(base_no_ts) == normalized_selected:
                return (Path(LOG_DIR) / f).read_text(encoding="utf-8")

    return "⚠️ No matching report found."


def delete_markdown_report(selected_title: str) -> bool:
    if not selected_title:
        print("❌ Title is None")
        return False

    def normalize(text: str) -> str:
        return text.lower().replace(" ", "_").strip()

    normalized_title = normalize(selected_title)
    print(f"🔍 Looking for files matching: {normalized_title}")

    matched_files = []
    for f in os.listdir(LOG_DIR):
        if not f.endswith(".md"):
            continue
        title_part = "_".join(f.rsplit("_", 2)[:-2])
        if normalize(title_part) == normalized_title:
            matched_files.append(f)

    if not matched_files:
        print("❌ No matching files found.")
        return False

    def extract_timestamp(f):
        import re
        match = re.search(r'_(\d{8}_\d{6})\.md$', f)
        return match.group(1) if match else ""

    matched_files.sort(key=extract_timestamp, reverse=True)
    file_to_delete = Path(LOG_DIR) / matched_files[0]

    print(f"🗑️ Deleting file: {file_to_delete}")
    try:
        file_to_delete.unlink()
        print("✅ File deleted.")
        return True
    except Exception as e:
        print(f"❌ Failed to delete: {e}")
        return False
