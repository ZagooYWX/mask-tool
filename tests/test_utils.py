"""测试文本工具函数"""

from mask_tool.utils.text import normalize_text, fuzzy_amount


class TestNormalizeText:
    """文本归一化测试"""

    def test_fullwidth_digits(self):
        assert normalize_text("１２３") == "123"

    def test_fullwidth_letters(self):
        assert normalize_text("ＡＢＣ") == "ABC"

    def test_extra_whitespace(self):
        assert normalize_text("hello   world") == "hello world"

    def test_mixed(self):
        result = normalize_text("金额：１.２亿元")
        assert "１" not in result
        assert "1" in result


class TestFuzzyAmount:
    """金额模糊化测试"""

    def test_yi_amount(self):
        assert fuzzy_amount("1.2亿元") == "1亿+"

    def test_wan_amount(self):
        assert fuzzy_amount("500万元") == "500万+"

    def test_yuan_amount(self):
        assert fuzzy_amount("1,234.56元") == "1234元+"

    def test_no_change(self):
        assert fuzzy_amount("普通文本") == "普通文本"
