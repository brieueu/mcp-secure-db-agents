from __future__ import annotations


def extract_sql(text: str) -> str:
    text = text.strip()
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            candidate = part.replace("sql", "", 1).strip()
            if candidate.lower().startswith("select"):
                return candidate
    marker = text.lower().find("select")
    if marker >= 0:
        return text[marker:].strip()
    return text
