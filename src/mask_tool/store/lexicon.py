"""词库管理 - 加载和管理敏感词词库与白名单"""

from pathlib import Path
from typing import Dict, List, Optional, Set

import yaml


class LexiconStore:
    """词库管理器"""

    def __init__(self, lexicon_path: str, whitelist_path: str = ""):
        self.lexicon_path = Path(lexicon_path)
        self.whitelist_path = Path(whitelist_path) if whitelist_path else None
        self._lexicon: Dict[str, List[str]] = {}
        self._whitelist: Set[str] = set()
        self._load()

    def _load(self) -> None:
        """加载词库和白名单"""
        # 加载词库
        if self.lexicon_path.exists():
            with open(self.lexicon_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            self._lexicon = {k: v for k, v in data.items() if isinstance(v, list)}

        # 加载白名单
        if self.whitelist_path and self.whitelist_path.exists():
            with open(self.whitelist_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            self._whitelist = set(data.get("whitelist", []))

    def get_lexicon(self) -> Dict[str, List[str]]:
        """获取词库"""
        return dict(self._lexicon)

    def get_whitelist(self) -> Set[str]:
        """获取白名单"""
        return set(self._whitelist)

    def add_word(self, category: str, word: str) -> None:
        """添加敏感词到词库"""
        if category not in self._lexicon:
            self._lexicon[category] = []
        if word not in self._lexicon[category]:
            self._lexicon[category].append(word)

    def add_to_whitelist(self, word: str) -> None:
        """添加词到白名单"""
        self._whitelist.add(word)

    def save(self) -> None:
        """保存词库和白名单到文件"""
        if self.lexicon_path.exists():
            with open(self.lexicon_path, "w", encoding="utf-8") as f:
                yaml.dump(self._lexicon, f, allow_unicode=True, default_flow_style=False)

        if self.whitelist_path and self.whitelist_path.exists():
            data = {"whitelist": list(self._whitelist)}
            with open(self.whitelist_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
