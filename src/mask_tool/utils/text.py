"""文本处理工具函数"""

import re


def normalize_text(text: str) -> str:
    """
    文本归一化：统一全角半角、去除多余空白

    Args:
        text: 原始文本

    Returns:
        归一化后的文本
    """
    # 全角转半角（数字和英文字母）
    text = text.translate(str.maketrans(
        "０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ",
        "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    ))
    # 去除多余空白
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def fuzzy_amount(text: str) -> str:
    """
    金额模糊化：将精确金额转换为模糊金额

    Examples:
        "1.2亿元" → "1亿+"
        "500万元" → "500万+"
        "1,234.56元" → "1000元+"
    """
    # 匹配金额模式
    patterns = [
        (r'(\d+)\.?\d*亿元', lambda m: f"{int(float(m.group(1)))}亿+"),
        (r'(\d+)\.?\d*万元', lambda m: f"{int(float(m.group(1)))}万+"),
        (r'(\d[\d,]*)\.?\d*元', lambda m: f"{int(float(m.group(1).replace(',', '')))}元+"),
    ]

    result = text
    for pattern, replacement in patterns:
        result = re.sub(pattern, replacement, result)

    return result
