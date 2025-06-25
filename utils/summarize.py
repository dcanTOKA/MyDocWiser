import re


def summarize_title(query: str) -> str:
    query = query.strip().lower()
    query = re.sub(r'[^a-zA-Z0-9\s]', '', query)
    query = re.sub(r'\s+', ' ', query)
    return query[:50].strip().capitalize()
