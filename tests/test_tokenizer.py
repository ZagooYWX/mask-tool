"""测试Token生成器"""

from mask_tool.core.tokenizer import TokenGenerator
from mask_tool.models.detection import DetectionType


class TestTokenGenerator:
    """Token生成器测试"""

    def setup_method(self):
        self.gen = TokenGenerator()

    def test_generate_company_token(self):
        """测试公司类Token生成"""
        token = self.gen.generate("某某建设集团有限公司", DetectionType.COMPANY)
        assert token == "[COMPANY_001]"

    def test_generate_person_token(self):
        """测试人名类Token生成"""
        token = self.gen.generate("张三", DetectionType.PERSON)
        assert token == "[PERSON_001]"

    def test_incrementing(self):
        """测试递增编号"""
        t1 = self.gen.generate("公司A", DetectionType.COMPANY)
        t2 = self.gen.generate("公司B", DetectionType.COMPANY)
        assert t1 == "[COMPANY_001]"
        assert t2 == "[COMPANY_002]"

    def test_same_text_same_token(self):
        """测试同一原文返回相同Token"""
        t1 = self.gen.generate("张三", DetectionType.PERSON)
        t2 = self.gen.generate("张三", DetectionType.PERSON)
        assert t1 == t2

    def test_independent_counters(self):
        """测试不同类别独立计数"""
        t1 = self.gen.generate("公司A", DetectionType.COMPANY)
        t2 = self.gen.generate("张三", DetectionType.PERSON)
        t3 = self.gen.generate("公司B", DetectionType.COMPANY)
        assert t1 == "[COMPANY_001]"
        assert t2 == "[PERSON_001]"
        assert t3 == "[COMPANY_002]"

    def test_get_all_mappings(self):
        """测试获取所有映射"""
        self.gen.generate("公司A", DetectionType.COMPANY)
        self.gen.generate("张三", DetectionType.PERSON)
        mappings = self.gen.get_all_mappings()
        assert mappings == {"公司A": "[COMPANY_001]", "张三": "[PERSON_001]"}

    def test_reset(self):
        """测试重置"""
        self.gen.generate("公司A", DetectionType.COMPANY)
        self.gen.reset()
        t = self.gen.generate("公司B", DetectionType.COMPANY)
        assert t == "[COMPANY_001]"  # 重置后从001开始
