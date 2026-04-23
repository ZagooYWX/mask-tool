"""jieba NER实现 - 基于jieba分词的词性标注进行命名实体识别"""

import re
from typing import Dict, List, Optional, Set

from mask_tool.core.ner.base import BaseNER
from mask_tool.models.detection import DetectionResult, DetectionType, Location


class JiebaNER(BaseNER):
    """
    基于jieba posseg的NER引擎

    利用jieba的词性标注功能识别：
    - nr/ns/nrt → 人名 (person)
    - ns → 地名 (location)
    - nt/ni/nis → 机构名 (company/government)
    - nz → 其他专名 (project/subject)

    优点：轻量（19MB）、零额外依赖、安装即用
    缺点：准确率不如深度学习模型，对未登录词识别能力有限
    """

    # jieba词性 → DetectionType映射
    POS_TYPE_MAP = {
        # 人名
        "nr": DetectionType.PERSON,      # 人名
        "nrfg": DetectionType.PERSON,    # 人名（古语）
        "nrt": DetectionType.PERSON,     # 人名（日语）
        # 地名
        "ns": DetectionType.LOCATION,    # 地名
        "nsf": DetectionType.LOCATION,   # 地名（外国）
        # 机构名
        "nt": DetectionType.COMPANY,     # 机构团体名
        "ni": DetectionType.COMPANY,     # 机构名
        "nis": DetectionType.COMPANY,    # 机构名（缩写）
        "nic": DetectionType.COMPANY,    # 机构名（下属）
        # 其他专名
        "nz": DetectionType.CUSTOM,      # 其他专名
    }

    # 需要过滤的短词（避免误识别）
    MIN_LENGTH = 2

    def __init__(self, user_dict: Optional[str] = None):
        """
        Args:
            user_dict: jieba自定义词典路径
        """
        self._available = False
        self._user_dict = user_dict
        self._whitelist: Set[str] = set()
        self._init_jieba()

    def _init_jieba(self) -> None:
        """初始化jieba，加载自定义词典"""
        try:
            import jieba
            import jieba.posseg as pseg

            self._jieba = jieba
            self._pseg = pseg

            # 加载自定义词典
            if self._user_dict:
                jieba.load_userdict(self._user_dict)

            self._available = True
        except ImportError:
            self._available = False

    def set_whitelist(self, whitelist: Set[str]) -> None:
        """设置白名单"""
        self._whitelist = whitelist

    def is_available(self) -> bool:
        return self._available

    def recognize(self, text: str, file_path: str = "") -> List[DetectionResult]:
        """
        对文本执行NER识别

        Args:
            text: 待识别文本
            file_path: 文件路径

        Returns:
            检测结果列表
        """
        if not self._available or not text.strip():
            return []

        results: List[DetectionResult] = []
        seen: Set[str] = set()

        # 使用jieba posseg进行词性标注
        words = self._pseg.cut(text)

        for word, flag in words:
            # 过滤条件
            if len(word) < self.MIN_LENGTH:
                continue
            if word in self._whitelist:
                continue
            if word in seen:
                continue

            # 查找映射的实体类型
            det_type = self.POS_TYPE_MAP.get(flag)
            if det_type is None:
                continue

            # 计算置信度（jieba NER置信度相对较低）
            confidence = self._calc_confidence(word, flag, det_type)

            # 提取上下文
            idx = text.find(word)
            if idx == -1:
                continue
            start = max(0, idx - 50)
            end = min(len(text), idx + len(word) + 50)
            context = text[start:end]

            results.append(DetectionResult(
                text=word,
                text_type=det_type,
                source="ner",
                confidence=confidence,
                location=Location(file=file_path),
                context=context,
            ))
            seen.add(word)

        return results

    def _calc_confidence(self, word: str, flag: str, det_type: DetectionType) -> float:
        """
        计算NER识别的置信度

        jieba的NER不如深度学习模型准确，所以置信度相对较低
        """
        # 基础置信度
        base = 0.60

        # 长词更可能是真实实体
        if len(word) >= 4:
            base += 0.10
        elif len(word) >= 3:
            base += 0.05

        # 机构名(nt)通常更准确
        if flag in ("nt", "ni", "nis"):
            base += 0.05

        # 人名(nr)在中文中相对准确
        if flag == "nr":
            base += 0.05

        # 地名(ns)准确度中等
        if flag == "ns":
            base += 0.03

        # 包含常见实体后缀的词更可信
        entity_suffixes = [
            "公司", "集团", "银行", "分行", "研究院", "大学",
            "政府", "委员会", "部门", "局", "部",
            "项目", "工程", "煤矿", "矿区",
        ]
        for suffix in entity_suffixes:
            if word.endswith(suffix):
                base += 0.08
                break

        return min(base, 0.85)  # jieba NER最高不超过0.85

    def add_words(self, words: List[tuple]) -> None:
        """
        动态添加词到jieba词典

        Args:
            words: [(word, freq, tag), ...] 列表
                   例如 [("某某银行某分行", 10, "nt")]
        """
        if not self._available:
            return
        for item in words:
            if len(item) == 3:
                self._jieba.add_word(item[0], freq=item[1], tag=item[2])
            elif len(item) == 2:
                self._jieba.add_word(item[0], tag=item[1])
            else:
                self._jieba.add_word(item[0])
