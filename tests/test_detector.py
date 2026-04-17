"""测试检测引擎"""

from mask_tool.core.detector import Detector
from mask_tool.models.detection import DetectionType


class TestDetector:
    """检测引擎测试"""

    def setup_method(self):
        lexicon = {
            "company": ["某某建设集团有限公司", "华为技术有限公司"],
            "person": ["张三"],
            "project": ["某某新区基础设施建设项目"],
            "location": ["某某市某某区"],
        }
        whitelist = {"有限公司"}
        self.detector = Detector(lexicon, whitelist)

    def test_dictionary_detection(self):
        """测试词库匹配"""
        results = self.detector.detect("甲方：某某建设集团有限公司")
        assert len(results) >= 1
        # "有限公司"在白名单中，不应单独匹配
        company_results = [r for r in results if r.text == "某某建设集团有限公司"]
        assert len(company_results) == 1
        assert company_results[0].text_type == DetectionType.COMPANY
        assert company_results[0].source == "dictionary"
        assert company_results[0].confidence == 0.95

    def test_regex_amount_detection(self):
        """测试金额正则匹配"""
        results = self.detector.detect("合同金额：1.2亿元")
        amount_results = [r for r in results if r.text_type == DetectionType.AMOUNT]
        assert len(amount_results) >= 1

    def test_regex_phone_detection(self):
        """测试手机号正则匹配"""
        results = self.detector.detect("联系电话：13812345678")
        phone_results = [r for r in results if "13812345678" in r.text]
        assert len(phone_results) == 1

    def test_regex_id_card_detection(self):
        """测试身份证号正则匹配"""
        results = self.detector.detect("身份证号：110101199001011234")
        id_results = [r for r in results if "110101199001011234" in r.text]
        assert len(id_results) >= 1
        # 身份证正则（17位+X）应匹配到
        id_card_hits = [r for r in id_results if r.confidence == 0.85]
        assert len(id_card_hits) == 1

    def test_whitelist_filtering(self):
        """测试白名单过滤"""
        results = self.detector.detect("某某建设集团有限公司")
        # "有限公司"不应作为独立匹配项
        standalone_results = [r for r in results if r.text == "有限公司"]
        assert len(standalone_results) == 0

    def test_empty_text(self):
        """测试空文本"""
        results = self.detector.detect("")
        assert len(results) == 0

    def test_no_matches(self):
        """测试无匹配文本"""
        results = self.detector.detect("这是一段普通文本，没有任何敏感信息。")
        assert len(results) == 0

    def test_location_info(self):
        """测试位置信息记录"""
        results = self.detector.detect("张三", file_path="test.docx")
        assert len(results) == 1
        assert results[0].location.file == "test.docx"

    def test_context_extraction(self):
        """测试上下文提取"""
        text = "甲方：某某建设集团有限公司，乙方：华为技术有限公司"
        results = self.detector.detect(text)
        for r in results:
            assert len(r.context) > 0
