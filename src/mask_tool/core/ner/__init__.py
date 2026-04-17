"""NER（命名实体识别）模块"""

from .base import BaseNER
from .jieba_ner import JiebaNER

__all__ = ["BaseNER", "JiebaNER"]
