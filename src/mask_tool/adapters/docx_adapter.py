"""Word文档(.docx)适配器"""

import copy
from pathlib import Path
from typing import List

from docx import Document

from mask_tool.adapters.base import FileAdapter
from mask_tool.models.detection import DetectionResult, Location


class DocxAdapter(FileAdapter):
    """Word文档脱敏适配器"""

    def supported_extensions(self) -> list[str]:
        return [".docx"]

    def process(self, input_path: Path, output_dir: Path) -> Path:
        """
        处理Word文档：
        - 遍历所有段落和表格
        - 在run级别进行文本替换（保持格式）
        """
        doc = Document(str(input_path))
        file_name = input_path.stem
        output_path = output_dir / f"{file_name}_masked.docx"

        # 处理段落
        for para_idx, paragraph in enumerate(doc.paragraphs):
            self._process_paragraph(paragraph, str(input_path), paragraph_index=para_idx)

        # 处理表格
        for table in doc.tables:
            for row_idx, row in enumerate(table.rows):
                for cell_idx, cell in enumerate(row.cells):
                    for para_idx, paragraph in enumerate(cell.paragraphs):
                        self._process_paragraph(
                            paragraph, str(input_path),
                            paragraph_index=para_idx,
                            cell_ref=f"R{row_idx + 1}C{cell_idx + 1}",
                        )

        output_dir.mkdir(parents=True, exist_ok=True)
        doc.save(str(output_path))
        return output_path

    def _process_paragraph(
        self,
        paragraph,
        file_path: str,
        paragraph_index: int = None,
        cell_ref: str = None,
    ) -> None:
        """处理单个段落中的所有run"""
        # 先收集完整段落文本用于检测
        full_text = paragraph.text
        if not full_text.strip():
            return

        # 检测
        results = self.detector.detect(full_text, file_path)

        # 为每条结果设置位置信息
        for r in results:
            r.location.paragraph = paragraph_index
            r.location.cell_ref = cell_ref

        # 策略决策
        results = self.policy.apply(results)

        # 在run级别执行替换
        for result in results:
            if result.text in full_text:
                self._replace_in_runs(paragraph, result.text, result)

    def _replace_in_runs(
        self,
        paragraph,
        original: str,
        result: DetectionResult,
    ) -> None:
        """在段落的run中替换文本，保持格式"""
        from mask_tool.models.detection import DetectionStatus

        if result.status not in (DetectionStatus.AUTO_MASK, DetectionStatus.SUGGEST_MASK):
            return

        # 获取替换文本
        if self.masker.irreversible:
            replacement = "***"
        else:
            from mask_tool.models.mapping import TokenMapping
            replacement = self.masker.token_gen.generate(result.text, result.text_type)
            self.masker.mappings.append(TokenMapping(
                token=replacement,
                original=result.text,
                text_type=result.text_type,
                confidence=result.confidence,
            ))

        # 在run中查找并替换
        runs_text = "".join(run.text for run in paragraph.runs)
        if original not in runs_text:
            return

        # 找到包含目标文本的run并替换
        remaining = original
        for run in paragraph.runs:
            if not remaining:
                break
            if remaining in run.text:
                run.text = run.text.replace(remaining, replacement, 1)
                remaining = ""
            elif run.text in remaining:
                run.text = replacement
                remaining = remaining[len(run.text):]
