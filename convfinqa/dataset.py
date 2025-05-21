from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Dict, List, Sequence

from .utils import stringify


class FinQADataset:
    """Thin wrapper around the ConvFinQA JSON dataset."""

    def __init__(self, file_path: str | Path) -> None:
        self._path: Path = Path(file_path).expanduser().resolve()
        self._data: List[Dict[str, Any]] = self._load()


    def sample(self, k: int | None = None, seed: int | None = None) -> Sequence[Dict[str, Any]]:
        """Return *k* random samples (or the entire dataset if *k* is None)."""
        data = self._data
        if k is None or k >= len(data):
            return data
        rng = random.Random(seed)
        return rng.sample(data, k)


    def _load(self) -> List[Dict[str, Any]]:
        if not self._path.is_file():
            raise FileNotFoundError(self._path)
        with self._path.open(encoding="utf-8") as fp:
            return json.load(fp)


    @staticmethod
    def build_context(entry: Dict[str, Any]) -> str:
        """Assemble a single context string for the LLM."""
        pre = stringify(entry.get("pre_text", ""))
        post = stringify(entry.get("post_text", ""))

        tbl_clean = json.dumps(entry.get("table", {}), ensure_ascii=False)
        return (
            "# Start of Context #\n"
            "Pre-Text:\n"
            f"{pre}\n\n"
            "Post-Text:\n"
            f"{post}\n\n"
            "Clean Table:\n"
            f"{tbl_clean}\n"
            "# End of Context #"
        )
