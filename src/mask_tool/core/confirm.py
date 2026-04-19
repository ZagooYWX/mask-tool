"""交互式确认模块 - 逐条确认检测结果"""

from typing import Dict, List, Optional, Set, Tuple

from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from mask_tool.models.detection import DetectionResult, DetectionStatus, DetectionType

console = Console()


class ConfirmEngine:
    """交互式确认引擎"""

    # DetectionType → 词库类别的映射
    TYPE_TO_CATEGORY = {
        DetectionType.COMPANY: "company",
        DetectionType.GOVERNMENT: "government",
        DetectionType.PERSON: "person",
        DetectionType.PROJECT: "project",
        DetectionType.SUBJECT: "subject",
        DetectionType.LOCATION: "location",
        DetectionType.AMOUNT: "amount",
        DetectionType.CUSTOM: "custom",
    }

    def __init__(self, auto_yes: bool = False):
        """
        Args:
            auto_yes: 是否自动确认所有（批量模式）
        """
        self.auto_yes = auto_yes
        self.confirmed: List[DetectionResult] = []
        self.skipped: List[DetectionResult] = []
        self.learned: List[Tuple[str, str]] = []  # [(text, category), ...]

    def confirm_batch(
        self,
        results: List[DetectionResult],
        file_name: str = "",
    ) -> List[DetectionResult]:
        """
        批量确认检测结果

        Args:
            results: 检测结果列表
            file_name: 当前文件名（用于展示）

        Returns:
            用户确认要脱敏的结果列表
        """
        if not results:
            return []

        if self.auto_yes:
            console.print(f"  [dim]自动确认 {len(results)} 项[/dim]")
            return list(results)

        console.print(f"\n  [bold]文件: {file_name}[/bold] — 共 {len(results)} 项待确认\n")

        # 先按类别分组展示
        self._print_grouped_table(results)

        console.print("\n  [bold]操作说明:[/bold]")
        console.print("    [green]Y[/green] = 确认脱敏  [red]N[/red] = 跳过  [blue]A[/blue] = 加入词库并脱敏  [dim]Q[/dim] = 退出\n")

        confirmed = []
        for i, result in enumerate(results, 1):
            action = self._confirm_single(result, i, len(results))
            if action == "quit":
                console.print("\n  [yellow]用户退出，已确认的项仍会执行脱敏[/yellow]")
                break
            elif action == "yes":
                confirmed.append(result)
                result.status = DetectionStatus.AUTO_MASK
            elif action == "learn":
                confirmed.append(result)
                result.status = DetectionStatus.AUTO_MASK
                category = self.TYPE_TO_CATEGORY.get(result.text_type, "custom")
                self.learned.append((result.text, category))
            else:  # skip
                result.status = DetectionStatus.HINT_ONLY

        self.confirmed.extend(confirmed)
        self.skipped.extend(r for r in results if r.status == DetectionStatus.HINT_ONLY)

        console.print(f"\n  [green]确认脱敏: {len(confirmed)} 项[/green] | "
                      f"[dim]跳过: {len(results) - len(confirmed)} 项[/dim]")
        if self.learned:
            console.print(f"  [blue]新学词: {len(self.learned)} 个[/blue]（将写入词库）")

        return confirmed

    def _confirm_single(
        self,
        result: DetectionResult,
        index: int,
        total: int,
    ) -> str:
        """确认单条结果，返回 'yes' / 'skip' / 'learn' / 'quit'"""
        source_tag = {
            "dictionary": "[dim]词典[/dim]",
            "ner": "[blue]NER[/blue]",
            "regex": "[yellow]正则[/yellow]",
        }.get(result.source, result.source)

        console.print(
            f"  [{index}/{total}] "
            f"[red bold]{result.text}[/red bold]  "
            f"类型={result.text_type.value}  "
            f"置信度={result.confidence:.2f}  "
            f"来源={source_tag}"
        )
        if result.context:
            # 高亮上下文中的敏感词
            highlighted = result.context.replace(result.text, f"[red bold]{result.text}[/red bold]")
            console.print(f"         上下文: {highlighted}")

        while True:
            choice = Prompt.ask(
                "         操作",
                choices=["y", "n", "a", "q", "Y", "N", "A", "Q"],
                default="y",
            ).lower()

            if choice == "y":
                return "yes"
            elif choice == "n":
                return "skip"
            elif choice == "a":
                console.print(f"         [blue]✓ '{result.text}' 将加入词库[/blue]")
                return "learn"
            elif choice == "q":
                return "quit"

    def _print_grouped_table(self, results: List[DetectionResult]) -> None:
        """按类别分组展示检测结果"""
        table = Table(show_lines=True, title="检测结果预览")
        table.add_column("#", style="dim", width=4)
        table.add_column("敏感信息", style="red bold")
        table.add_column("类别", width=12)
        table.add_column("来源", width=10)
        table.add_column("置信度", width=8)

        for i, r in enumerate(results, 1):
            table.add_row(
                str(i),
                r.text,
                r.text_type.value,
                r.source,
                f"{r.confidence:.2f}",
            )

        console.print(table)

    def get_learned_words(self) -> Dict[str, List[str]]:
        """
        获取学习到的词，按类别分组

        Returns:
            {"company": ["国开行", ...], "location": ["霍尔果斯", ...], ...}
        """
        grouped: Dict[str, List[str]] = {}
        for text, category in self.learned:
            if category not in grouped:
                grouped[category] = []
            if text not in grouped[category]:
                grouped[category].append(text)
        return grouped
