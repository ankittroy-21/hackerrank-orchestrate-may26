from pathlib import Path
import yaml
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import DATA_DIR, COMPANIES

def load_documents() -> list[dict]:
    docs = []
    for md_file in DATA_DIR.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
            parts = content.split("---")
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1]) or {}
                body = "---".join(parts[2:]).strip()
            else:
                frontmatter = {}
                body = content.strip()

            path_str = str(md_file).replace("\\", "/")
            company = "Unknown"
            for c in COMPANIES:
                if f"/data/{c.lower()}/" in path_str.lower():
                    company = c
                    break

            docs.append({
                "title":       frontmatter.get("title", md_file.stem),
                "source_url":  frontmatter.get("source_url", ""),
                "breadcrumbs": frontmatter.get("breadcrumbs", []),
                "company":     company,
                "body":        body,
                "filepath":    str(md_file)
            })
        except Exception:
            continue
    return docs
