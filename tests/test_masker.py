"""测试脱敏执行器"""

from mask_tool.core.masker import Masker
from mask_tool.core.tokenizer import TokenGenerator
from mask_tool.models.detection import (
    DetectionResult, DetectionType, DetectionStatus, Location,
)


class TestMasker:
    """脱敏执行器测试"""

    def setup_method(self):
        self.token_gen = TokenGenerator()
        self.masker = Masker(self.token_gen, irreversible=False)

    def test_reversible_masking(self):
        """测试可逆脱敏"""
        results = [
            DetectionResult(
                text="某某建设集团有限公司",
                text_type=DetectionType.COMPANY,
                source="dictionary",
                confidence=0.95,
                location=Location(file="test.docx"),
                status=DetectionStatus.AUTO_MASK,
            ),
        ]
        masked = self.masker.mask_text("甲方：某某建设集团有限公司", results)
        assert "某某建设集团有限公司" not in masked
        assert "[COMPANY_001]" in masked

    def test_irreversible_masking(self):
        """测试不可逆脱敏"""
        masker = Masker(TokenGenerator(), irreversible=True)
        results = [
            DetectionResult(
                text="张三",
                text_type=DetectionType.PERSON,
                source="dictionary",
                confidence=0.95,
                location=Location(file="test.docx"),
                status=DetectionStatus.AUTO_MASK,
            ),
        ]
        masked = masker.mask_text("负责人：张三", results)
        assert "张三" not in masked
        assert "***" in masked

    def test_hint_only_not_masked(self):
        """测试仅提示的项不被脱敏"""
        results = [
            DetectionResult(
                text="张三",
                text_type=DetectionType.PERSON,
                source="dictionary",
                confidence=0.50,
                location=Location(file="test.docx"),
                status=DetectionStatus.HINT_ONLY,
            ),
        ]
        masked = self.masker.mask_text("负责人：张三", results)
        assert "张三" in masked

    def test_multiple_matches(self):
        """测试多个匹配项"""
        results = [
            DetectionResult(
                text="某某建设集团有限公司",
                text_type=DetectionType.COMPANY,
                source="dictionary",
                confidence=0.95,
                location=Location(file="test.docx"),
                status=DetectionStatus.AUTO_MASK,
            ),
            DetectionResult(
                text="张三",
                text_type=DetectionType.PERSON,
                source="dictionary",
                confidence=0.95,
                location=Location(file="test.docx"),
                status=DetectionStatus.AUTO_MASK,
            ),
        ]
        masked = self.masker.mask_text("甲方：某某建设集团有限公司，负责人：张三", results)
        assert "[COMPANY_001]" in masked
        assert "[PERSON_001]" in masked

    def test_get_mappings(self):
        """测试获取映射关系"""
        results = [
            DetectionResult(
                text="张三",
                text_type=DetectionType.PERSON,
                source="dictionary",
                confidence=0.95,
                location=Location(file="test.docx"),
                status=DetectionStatus.AUTO_MASK,
            ),
        ]
        self.masker.mask_text("负责人：张三", results)
        mappings = self.masker.get_mappings()
        assert len(mappings) == 1
        assert mappings[0].token == "[PERSON_001]"
        assert mappings[0].original == "张三"
