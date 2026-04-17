"""Token生成器 - 生成可逆脱敏的唯一Token"""

from typing import Dict

from mask_tool.models.detection import DetectionType


class TokenGenerator:
    """按类别生成递增编号的Token，如 [COMPANY_001]"""

    # 类别前缀映射
    TYPE_PREFIX = {
        DetectionType.COMPANY: "COMPANY",
        DetectionType.GOVERNMENT: "GOVERNMENT",
        DetectionType.PERSON: "PERSON",
        DetectionType.PROJECT: "PROJECT",
        DetectionType.SUBJECT: "SUBJECT",
        DetectionType.LOCATION: "LOCATION",
        DetectionType.AMOUNT: "AMOUNT",
        DetectionType.CUSTOM: "CUSTOM",
    }

    def __init__(self):
        self._counters: Dict[str, int] = {}
        self._token_map: Dict[str, str] = {}  # original -> token

    def generate(self, original: str, text_type: DetectionType) -> str:
        """
        为原文生成Token。同一原文在同一次运行中返回相同Token。

        Args:
            original: 原始文本
            text_type: 敏感信息类别

        Returns:
            Token字符串，如 "[COMPANY_001]"
        """
        # 同一原文复用Token
        if original in self._token_map:
            return self._token_map[original]

        prefix = self.TYPE_PREFIX.get(text_type, "CUSTOM")
        counter = self._counters.get(prefix, 0) + 1
        self._counters[prefix] = counter

        token = f"[{prefix}_{counter:03d}]"
        self._token_map[original] = token
        return token

    def get_all_mappings(self) -> Dict[str, str]:
        """获取所有 original -> token 映射"""
        return dict(self._token_map)

    def reset(self) -> None:
        """重置所有计数器和映射"""
        self._counters.clear()
        self._token_map.clear()
