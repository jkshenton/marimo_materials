"""MkDocs hook: copy raw markdown sources into the built site.

This makes paths like /reference/crystal-viewer.md resolve during both
`mkdocs serve` (development) and `mkdocs build` (production).

The post-build step in `scripts/copy_docs_md.py` will later overwrite these
with polished versions extracted from the rendered HTML when running
`make docs`.
"""

from __future__ import annotations

import fnmatch
import shutil
from pathlib import Path


def on_post_build(config: dict, **kwargs) -> None:
    docs_dir = Path(config["docs_dir"])
    site_dir = Path(config["site_dir"])
    exclude_spec = config.get("exclude_docs")

    def _is_excluded(relative: str) -> bool:
        if exclude_spec is None:
            return False
        # Modern MkDocs: GitIgnoreSpec
        if hasattr(exclude_spec, "match_file"):
            return bool(exclude_spec.match_file(relative))
        # Older MkDocs: list/string of patterns
        patterns = exclude_spec if not isinstance(exclude_spec, str) else [p.strip() for p in exclude_spec.split(",")]
        return any(fnmatch.fnmatch(relative, pat) for pat in patterns)

    for source in sorted(docs_dir.rglob("*.md")):
        relative = source.relative_to(docs_dir).as_posix()
        if _is_excluded(relative):
            continue
        destination = site_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
