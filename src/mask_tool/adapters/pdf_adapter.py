"""PDF适配器 - MVP阶段仅提取文本并生成脱敏报告，不做回写"""

import json
from pathlib import Path

import fitz  # PyMuPDF

from mask_tool.adapters.base import FileAdapter
from mask_tool.models.detection import DetectionResult, Location


class PdfAdapter(FileAdapter):
    """PDF文档适配器（MVP: 仅文本提取+报告）"""

    def __init__(self, detector, policy, masker=None):
        # PDF适配器MVP阶段不需要masker
        super().__init__(detector, policy, masker)

    def supported_extensions(self) -> list[str]:
        return [".pdf"]

    def process(self, input_path: Path, output_dir: Path) -> Path:
        """
        处理PDF文档：
        - 逐页提取文本
        - 检测敏感信息
        - 输出脱敏报告（不做PDF回写）
        """
        doc = fitz.open(str(input_path))
        file_name = input_path.stem
        output_path = output_dir / f"{file_name}_masked_report.json"

        all_results = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if not text.strip():
                continue

            # 检测
            results = self.detector.detect(text, str(input_path))
            for r in results:
                r.location.page = page_num + 1

            # 策略决策
            results = self.policy.apply(results)
            all_results.extend(results)

        # 输出报告
        output_dir.mkdir(parents=True, exist_ok=True)
        report_data = {
            "file": str(input_path),
            "total_pages": len(doc),
            "total_detections": len(all_results),
            "detections": [
                {
                    "text": r.text,
                    "type": r.text_type.value,
                    "source": r.source,
                    "confidence": r.confidence,
                    "status": r.status.value,
                    "page": r.location.page,
                    "context": r.context,
                }
                for r in all_results
            ],
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)

        doc.close()
        return output_path
