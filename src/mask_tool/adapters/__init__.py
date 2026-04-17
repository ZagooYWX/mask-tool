"""文件格式适配器"""

from .base import FileAdapter
from .docx_adapter import DocxAdapter
from .xlsx_adapter import XlsxAdapter
from .pptx_adapter import PptxAdapter

__all__ = ["FileAdapter", "DocxAdapter", "XlsxAdapter", "PptxAdapter"]


def get_pdf_adapter():
    """延迟导入PDF适配器（依赖PyMuPDF）"""
    try:
        from .pdf_adapter import PdfAdapter
        return PdfAdapter
    except ImportError:
        return None
