"""CLI命令行入口"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

app = typer.Typer(
    name="mask-tool",
    help="本地文件脱敏工具 - 支持可逆脱敏、智能识别、多格式办公文件处理",
    no_args_is_help=True,
)
console = Console()


@app.command()
def mask(
    input_path: Path = typer.Argument(..., help="输入文件或目录路径"),
    output: Path = typer.Option("./output", "--output", "-o", help="输出目录"),
    mode: str = typer.Option("smart", "--mode", "-m", help="运行模式: strict/smart/aggressive"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="配置文件路径"),
    irreversible: bool = typer.Option(False, "--irreversible", help="使用不可逆脱敏"),
) -> None:
    """对文件执行脱敏处理"""
    console.print(f"[bold green]mask-tool[/bold green] v0.1.0")
    console.print(f"输入: {input_path}")
    console.print(f"输出: {output}")
    console.print(f"模式: {mode}")
    console.print(f"不可逆: {irreversible}")

    # TODO: Phase 5 实现完整流水线
    console.print("[yellow]MVP开发中，此功能尚未实现...[/yellow]")


@app.command()
def unmask(
    input_path: Path = typer.Argument(..., help="脱敏后的文件路径"),
    mapping: Path = typer.Option(..., "--mapping", help="映射表文件路径(JSON)"),
    output: Path = typer.Option("./restored", "--output", "-o", help="输出目录"),
) -> None:
    """反脱敏：根据映射表还原原文"""
    console.print(f"[bold green]mask-tool[/bold green] v0.1.0")
    console.print(f"输入: {input_path}")
    console.print(f"映射表: {mapping}")
    console.print(f"输出: {output}")

    # TODO: Phase 5 实现反脱敏
    console.print("[yellow]MVP开发中，此功能尚未实现...[/yellow]")


@app.command()
def inspect(
    input_path: Path = typer.Argument(..., help="输入文件或目录路径"),
    config: Optional[Path] = typer.Option(None, "--config", "-c", help="配置文件路径"),
) -> None:
    """检测文件中的敏感信息（不执行脱敏）"""
    console.print(f"[bold green]mask-tool[/bold green] v0.1.0")
    console.print(f"输入: {input_path}")

    # TODO: Phase 2 实现检测引擎
    console.print("[yellow]MVP开发中，此功能尚未实现...[/yellow]")


@app.command()
def config_init(
    output: Path = typer.Option(".", "--output", "-o", help="输出目录"),
) -> None:
    """生成默认配置文件和示例词库"""
    console.print(f"[bold green]mask-tool[/bold green] v0.1.0")
    console.print(f"配置文件将输出到: {output}")

    # TODO: Phase 1 实现
    console.print("[yellow]MVP开发中，此功能尚未实现...[/yellow]")


@app.command()
def version() -> None:
    """显示版本信息"""
    from mask_tool import __version__
    console.print(f"mask-tool v{__version__}")
