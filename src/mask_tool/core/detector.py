"""检测引擎 - 正则规则 + 词典匹配"""

import re
from typing import Dict, List, Optional, Set

from mask_tool.models.detection import DetectionResult, DetectionType, Location


class Detector:
    """敏感信息检测引擎"""

    def __init__(self, lexicon: Dict[str, List[str]], whitelist: Set[str]):
        """
        Args:
            lexicon: 词库，key为类别名，value为敏感词列表
            whitelist: 白名单，这些词不会被匹配
        """
        self.lexicon = lexicon
        self.whitelist = whitelist
        self._regex_rules: List[tuple] = self._build_regex_rules()
        self._lexicon_patterns: List[tuple] = self._build_lexicon_patterns()

    def _build_regex_rules(self) -> List[tuple]:
        """构建正则规则列表: [(compiled_regex, DetectionType, confidence), ...]"""
        rules = [
            # 金额: 1.2亿, 500万, 1,234.56元
            (re.compile(r'[\d,]+\.?\d*[万亿]元?'), DetectionType.AMOUNT, 0.80),
            (re.compile(r'人民币\s*[\d,]+\.?\d*[万亿]?元?'), DetectionType.AMOUNT, 0.90),
            # 手机号
            (re.compile(r'1[3-9]\d{9}'), DetectionType.CUSTOM, 0.85),
            # 身份证号
            (re.compile(r'\d{17}[\dXx]'), DetectionType.CUSTOM, 0.85),
            # 邮箱
            (re.compile(r'[\w.-]+@[\w.-]+\.\w+'), DetectionType.CUSTOM, 0.75),
            # 日期
            (re.compile(r'\d{4}年\d{1,2}月\d{1,2}日'), DetectionType.CUSTOM, 0.70),
            # 银行卡号（简化）
            (re.compile(r'\d{16,19}'), DetectionType.CUSTOM, 0.65),
        ]
        return rules

    def _build_lexicon_patterns(self) -> List[tuple]:
        """构建词库匹配模式列表: [(text, DetectionType, confidence), ...]"""
        patterns = []
        type_map = {
            "company": DetectionType.COMPANY,
            "government": DetectionType.GOVERNMENT,
            "person": DetectionType.PERSON,
            "project": DetectionType.PROJECT,
            "subject": DetectionType.SUBJECT,
            "location": DetectionType.LOCATION,
            "amount": DetectionType.AMOUNT,
            "custom": DetectionType.CUSTOM,
        }
        for category, words in self.lexicon.items():
            det_type = type_map.get(category, DetectionType.CUSTOM)
            for word in words:
                if word not in self.whitelist:
                    patterns.append((word, det_type, 0.95))
        return patterns

    def detect(self, text: str, file_path: str = "") -> List[DetectionResult]:
        """
        对文本执行敏感信息检测

        Args:
            text: 待检测文本
            file_path: 文件路径（用于Location）

        Returns:
            检测结果列表
        """
        results: List[DetectionResult] = []

        # 1. 正则匹配
        for regex, det_type, confidence in self._regex_rules:
            for match in regex.finditer(text):
                matched_text = match.group()
                if matched_text not in self.whitelist:
                    start = max(0, match.start() - 50)
                    end = min(len(text), match.end() + 50)
                    context = text[start:end]
                    results.append(DetectionResult(
                        text=matched_text,
                        text_type=det_type,
                        source="regex",
                        confidence=confidence,
                        location=Location(file=file_path),
                        context=context,
                    ))

        # 2. 词库匹配
        for word, det_type, confidence in self._lexicon_patterns:
            if word in text:
                idx = text.index(word)
                start = max(0, idx - 50)
                end = min(len(text), idx + len(word) + 50)
                context = text[start:end]
                results.append(DetectionResult(
                    text=word,
                    text_type=det_type,
                    source="dictionary",
                    confidence=confidence,
                    location=Location(file=file_path),
                    context=context,
                ))

        return results
