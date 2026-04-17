"""文件格式适配器"""

from .base import FileAdapter
from .docx_adapter import DocxAdapter
from .xlsx_adapter import XlsxAdapter
from .pptx_adapter import PptxAdapter
from .pdf_adapter import PdfAdapter

__all__ = ["FileAdapter", "DocxAdapter", "XlsxAdapter", "PptxAdapter", "PdfAdapter"]
