"""测试策略引擎"""

from mask_tool.core.policy import PolicyEngine
from mask_tool.models.config import MaskConfig, Thresholds
from mask_tool.models.detection import (
    DetectionResult, DetectionType, DetectionStatus, Location,
)


class TestPolicyEngine:
    """策略引擎测试"""

    def _make_result(self, confidence: float) -> DetectionResult:
        return DetectionResult(
            text="测试",
            text_type=DetectionType.COMPANY,
            source="dictionary",
            confidence=confidence,
            location=Location(file="test.docx"),
        )

    def test_smart_mode_auto_mask(self):
        """smart模式：高置信度自动脱敏"""
        config = MaskConfig(mode="smart", thresholds=Thresholds(auto_mask=0.85, suggest_mask=0.6))
        engine = PolicyEngine(config)
        result = self._make_result(0.95)
        results = engine.apply([result])
        assert results[0].status == DetectionStatus.AUTO_MASK

    def test_smart_mode_suggest(self):
        """smart模式：中等置信度建议脱敏"""
        config = MaskConfig(mode="smart", thresholds=Thresholds(auto_mask=0.85, suggest_mask=0.6))
        engine = PolicyEngine(config)
        result = self._make_result(0.75)
        results = engine.apply([result])
        assert results[0].status == DetectionStatus.SUGGEST_MASK

    def test_smart_mode_hint(self):
        """smart模式：低置信度仅提示"""
        config = MaskConfig(mode="smart", thresholds=Thresholds(auto_mask=0.85, suggest_mask=0.6))
        engine = PolicyEngine(config)
        result = self._make_result(0.50)
        results = engine.apply([result])
        assert results[0].status == DetectionStatus.HINT_ONLY

    def test_strict_mode_strict(self):
        """strict模式：仅高置信度自动脱敏"""
        config = MaskConfig(mode="strict")
        engine = PolicyEngine(config)
        result = self._make_result(0.90)
        results = engine.apply([result])
        assert results[0].status == DetectionStatus.SUGGEST_MASK  # strict下0.90只是建议

    def test_aggressive_mode(self):
        """aggressive模式：降低阈值"""
        config = MaskConfig(mode="aggressive")
        engine = PolicyEngine(config)
        result = self._make_result(0.70)
        results = engine.apply([result])
        assert results[0].status == DetectionStatus.AUTO_MASK
