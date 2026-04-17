"""流水线编排 - 核心中的核心，串联所有模块"""

import json
import time
from pathlib import Path
from typing import List, Optional

from mask_tool.models.config import MaskConfig
from mask_tool.models.detection import DetectionResult, DetectionStatus
from mask_tool.models.report import MaskReport
from mask_tool.core.detector import Detector
from mask_tool.core.policy import PolicyEngine
from mask_tool.core.masker import Masker
from mask_tool.core.tokenizer import TokenGenerator
from mask_tool.store.lexicon import LexiconStore


class Pipeline:
    """脱敏处理流水线"""

    def __init__(self, config: MaskConfig):
        self.config = config
        self.report = MaskReport()

        # 加载词库
        lexicon_store = LexiconStore(config.lexicon_path, config.whitelist_path)
        lexicon = lexicon_store.get_lexicon()
        whitelist = lexicon_store.get_whitelist()

        # 初始化各引擎
        self.detector = Detector(lexicon, whitelist)
        self.policy = PolicyEngine(config)
        self.token_gen = TokenGenerator()
        self.masker = Masker(self.token_gen, irreversible=False)

    def process_text(self, text: str, file_path: str = "") -> str:
        """
        对纯文本执行完整的脱敏流水线

        Args:
            text: 原始文本
            file_path: 文件路径（用于报告）

        Returns:
            脱敏后的文本
        """
        # 1. 检测
        results = self.detector.detect(text, file_path)

        # 2. 策略决策
        results = self.policy.apply(results)

        # 3. 脱敏
        masked_text = self.masker.mask_text(text, results)

        # 4. 记录到报告
        for result in results:
            self.report.add_result(result)

        return masked_text

    def process_file(self, input_path: Path, output_dir: Path) -> Optional[Path]:
        """
        对单个文件执行脱敏处理

        Args:
            input_path: 输入文件路径
            output_dir: 输出目录

        Returns:
            输出文件路径，或None（如果不支持该格式）
        """
        suffix = input_path.suffix.lower()
        self.report.input_files.append(str(input_path))

        # 记录处理前的映射数量，用于计算本文件新增的脱敏项
        mappings_before = len(self.masker.mappings)

        # 根据文件类型选择适配器
        if suffix == ".docx":
            result = self._process_docx(input_path, output_dir)
        elif suffix == ".xlsx":
            result = self._process_xlsx(input_path, output_dir)
        elif suffix == ".pptx":
            result = self._process_pptx(input_path, output_dir)
        elif suffix == ".pdf":
            result = self._process_pdf(input_path, output_dir)
        else:
            return None

        # 将本文件新增的映射记录到报告
        from mask_tool.models.detection import DetectionStatus
        for m in self.masker.mappings[mappings_before:]:
            self.report.auto_masked.append({
                "text": m.original,
                "type": m.text_type.value,
                "source": "adapter",
                "confidence": m.confidence,
                "file": str(input_path),
                "token": m.token,
            })

        return result

    def _process_docx(self, input_path: Path, output_dir: Path) -> Path:
        """处理Word文档"""
        from mask_tool.adapters.docx_adapter import DocxAdapter
        adapter = DocxAdapter(self.detector, self.policy, self.masker)
        output_path = adapter.process(input_path, output_dir)
        self.report.output_files.append(str(output_path))
        return output_path

    def _process_xlsx(self, input_path: Path, output_dir: Path) -> Path:
        """处理Excel文档"""
        from mask_tool.adapters.xlsx_adapter import XlsxAdapter
        adapter = XlsxAdapter(self.detector, self.policy, self.masker)
        output_path = adapter.process(input_path, output_dir)
        self.report.output_files.append(str(output_path))
        return output_path

    def _process_pptx(self, input_path: Path, output_dir: Path) -> Path:
        """处理PowerPoint文档"""
        from mask_tool.adapters.pptx_adapter import PptxAdapter
        adapter = PptxAdapter(self.detector, self.policy, self.masker)
        output_path = adapter.process(input_path, output_dir)
        self.report.output_files.append(str(output_path))
        return output_path

    def _process_pdf(self, input_path: Path, output_dir: Path) -> Path:
        """处理PDF文档（MVP: 仅提取文本并生成报告）"""
        try:
            from mask_tool.adapters.pdf_adapter import PdfAdapter
        except ImportError:
            raise RuntimeError(
                "PDF处理需要安装PyMuPDF: pip install pymupdf"
            )
        adapter = PdfAdapter(self.detector, self.policy)
        output_path = adapter.process(input_path, output_dir)
        self.report.output_files.append(str(output_path))
        return output_path

    def save_mapping(self, output_path: Path) -> None:
        """保存映射表到JSON文件"""
        data = {
            "tokens": {},
            "metadata": {
                "total_mappings": len(self.masker.get_mappings()),
                "mode": self.config.mode,
            },
        }
        for m in self.masker.get_mappings():
            data["tokens"][m.token] = m.to_dict()

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def save_report(self, output_path: Path) -> None:
        """保存脱敏报告到JSON文件"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.report.to_dict(), f, ensure_ascii=False, indent=2)

    def get_report(self) -> MaskReport:
        """获取当前报告"""
        return self.report
