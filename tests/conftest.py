"""pytest共享fixtures"""

import pytest
from pathlib import Path


@pytest.fixture
def sample_text():
    """示例文本，包含各类敏感信息"""
    return """
    合同编号：HT-2024-001

    甲方：某某建设集团有限公司
    乙方：华为技术有限公司

    项目名称：某某新区基础设施建设项目
    项目负责人：张三

    合同金额：1.2亿元
    联系电话：13812345678
    身份证号：110101199001011234

    签约地点：某某市某某区
    签约日期：2024年3月15日
    """
