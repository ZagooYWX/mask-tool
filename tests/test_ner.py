"""测试NER引擎"""

from mask_tool.core.ner.jieba_ner import JiebaNER
from mask_tool.models.detection import DetectionType


class TestJiebaNER:
    """jieba NER引擎测试"""

    def setup_method(self):
        self.ner = JiebaNER()

    def test_is_available(self):
        """测试NER引擎可用性"""
        assert self.ner.is_available() is True

    def test_person_detection(self):
        """测试人名识别"""
        results = self.ner.recognize("项目负责人某人甲负责此事")
        persons = [r for r in results if r.text_type == DetectionType.PERSON]
        assert len(persons) >= 1
        assert "某人甲" in [p.text for p in persons]

    def test_location_detection(self):
        """测试地名识别"""
        results = self.ner.recognize("某市位于某省西部")
        locations = [r for r in results if r.text_type == DetectionType.LOCATION]
        assert len(locations) >= 1
        texts = [l.text for l in locations]
        assert any("某" in t or "省" in t for t in texts)

    def test_organization_detection(self):
        """测试机构名识别"""
        results = self.ner.recognize("某某银行某分行为该项目提供贷款")
        orgs = [r for r in results if r.text_type == DetectionType.COMPANY]
        assert len(orgs) >= 1

    def test_source_is_ner(self):
        """测试来源标记为ner"""
        results = self.ner.recognize("某人甲去了北京")
        for r in results:
            assert r.source == "ner"

    def test_confidence_range(self):
        """测试置信度在合理范围内"""
        results = self.ner.recognize("某人甲去了北京市海淀区")
        for r in results:
            assert 0.0 <= r.confidence <= 1.0

    def test_no_short_words(self):
        """测试不返回过短的词"""
        results = self.ner.recognize("这是一个测试")
        for r in results:
            assert len(r.text) >= 2

    def test_whitelist_filtering(self):
        """测试白名单过滤"""
        self.ner.set_whitelist({"有限公司"})
        results = self.ner.recognize("某某建设集团有限公司")
        # "有限公司"不应单独出现
        assert not any(r.text == "有限公司" for r in results)

    def test_empty_text(self):
        """测试空文本"""
        results = self.ner.recognize("")
        assert len(results) == 0

    def test_no_duplicates(self):
        """测试不返回重复结果"""
        results = self.ner.recognize("某人甲和某人甲去了北京和北京")
        texts = [r.text for r in results]
        assert len(texts) == len(set(texts))

    def test_real_world_text(self):
        """测试真实文本（示例文档片段）"""
        text = "某市已委托某公司编制项目方案"
        results = self.ner.recognize(text)
        # 应该能识别出至少一个地名或机构名
        assert len(results) >= 1
