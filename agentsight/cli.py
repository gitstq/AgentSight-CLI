"""CLI entry point for AgentSight-CLI.

Provides the command-line interface using Click framework
with Rich for beautiful terminal output.
"""

import sys
from typing import List, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich import box

from . import __version__
from .sources import get_source, get_all_sources, SOURCE_REGISTRY
from .extractors.html import HTMLExtractor
from .formatters import get_formatter
from .models import SourceItem

# Initialize Rich console
console = Console()


def _format_score(score: int) -> str:
    """Format a score number with human-readable suffixes.

    Args:
        score: The numeric score.

    Returns:
        Formatted score string.
    """
    if score >= 1000000:
        return f"{score / 1000000:.1f}M"
    elif score >= 1000:
        return f"{score / 1000:.1f}K"
    return str(score)


def _display_items_table(items: List[SourceItem], title: str = "Results") -> None:
    """Display items in a Rich table.

    Args:
        items: List of SourceItem objects to display.
        title: Table title.
    """
    if not items:
        console.print(Panel("[yellow]No items found.[/yellow]", title=title))
        return

    table = Table(
        title=title,
        box=box.ROUNDED,
        show_lines=True,
        title_style="bold cyan",
        header_style="bold magenta",
        width=min(console.width, 120),
    )

    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Title", style="bold white", max_width=50, no_wrap=False)
    table.add_column("Author", style="green", max_width=15)
    table.add_column("Score", style="yellow", justify="right", width=8)
    table.add_column("Comments", style="blue", justify="right", width=8)

    for i, item in enumerate(items, 1):
        table.add_row(
            str(i),
            item.title[:80],
            item.author[:20] if item.author else "-",
            _format_score(item.score),
            _format_score(item.comments),
        )

    console.print(table)

    # Show URLs below the table
    console.print()
    for i, item in enumerate(items, 1):
        console.print(f"  [dim]{i}.[/dim] [link={item.url}]{item.url}[/link]")


@click.group()
@click.version_option(version=__version__, prog_name="agentsight")
@click.option("--proxy", default="", help="HTTP proxy URL (e.g., http://127.0.0.1:7890)")
@click.option("--no-cache", is_flag=True, help="Disable response caching")
@click.option("--no-ssl-verify", is_flag=True, help="Disable SSL certificate verification")
@click.pass_context
def cli(ctx: click.Context, proxy: str, no_cache: bool, no_ssl_verify: bool) -> None:
    """AgentSight-CLI: Lightweight AI Agent multi-source web data collection engine.

    Give your AI Agent the "eyes" to read internet data.
    """
    ctx.ensure_object(dict)
    ctx.obj["proxy"] = proxy
    ctx.obj["no_cache"] = no_cache
    ctx.obj["no_ssl_verify"] = no_ssl_verify


@cli.command()
@click.argument("source")
@click.option("--limit", "-n", default=20, help="Maximum number of items to fetch")
@click.option("--format", "-f", "output_format", default="table",
              type=click.Choice(["table", "json", "markdown", "csv", "rag"]),
              help="Output format")
@click.option("--output", "-o", default=None, help="Output file path (default: stdout)")
@click.pass_context
def list_cmd(ctx: click.Context, source: str, limit: int, output_format: str, output: Optional[str]) -> None:
    """List trending/popular items from a data source.

    SOURCE: Data source name (github, reddit, hackernews, weibo, zhihu, bilibili)
    """
    try:
        source_instance = get_source(source)
    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)

    # Apply CLI options to config
    config = source_instance.config
    if ctx.obj.get("proxy"):
        config.set("proxy", ctx.obj["proxy"])
    if ctx.obj.get("no_cache"):
        config.set("cache_enabled", False)
    if ctx.obj.get("no_ssl_verify"):
        config.set("verify_ssl", False)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"Fetching from {source_instance.name}...", total=None)
        try:
            items = source_instance.fetch(limit=limit)
        except Exception as e:
            progress.stop()
            console.print(f"[red]Error fetching data:[/red] {e}")
            sys.exit(1)
        finally:
            progress.update(task, completed=True)

    if not items:
        console.print(Panel(f"[yellow]No items found from {source_instance.name}.[/yellow]",
                            title=source_instance.name))
        return

    # Output based on format
    if output_format == "table":
        _display_items_table(items, title=f"{source_instance.name} (Top {len(items)})")
    else:
        try:
            formatter = get_formatter(output_format)
            formatted = formatter.format_items(items)

            if output:
                with open(output, "w", encoding="utf-8") as f:
                    f.write(formatted)
                console.print(f"[green]Output saved to:[/green] {output}")
            else:
                console.print(formatted)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)


@cli.command()
@click.argument("keyword")
@click.option("--sources", "-s", default="all",
              help="Comma-separated source names or 'all' for all sources")
@click.option("--limit", "-n", default=10, help="Maximum items per source")
@click.option("--format", "-f", "output_format", default="table",
              type=click.Choice(["table", "json", "markdown", "csv", "rag"]),
              help="Output format")
@click.option("--output", "-o", default=None, help="Output file path (default: stdout)")
@click.pass_context
def search(ctx: click.Context, keyword: str, sources: str, limit: int,
           output_format: str, output: Optional[str]) -> None:
    """Search for items matching a keyword across data sources.

    KEYWORD: Search keyword to look for.
    """
    # Determine which sources to search
    if sources.lower() == "all":
        source_names = list(SOURCE_REGISTRY.keys())
    else:
        source_names = [s.strip() for s in sources.split(",")]

    all_items: List[SourceItem] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        for source_name in source_names:
            task = progress.add_task(f"Searching {source_name} for '{keyword}'...", total=None)
            try:
                source_instance = get_source(source_name)

                # Apply CLI options
                config = source_instance.config
                if ctx.obj.get("proxy"):
                    config.set("proxy", ctx.obj["proxy"])
                if ctx.obj.get("no_cache"):
                    config.set("cache_enabled", False)
                if ctx.obj.get("no_ssl_verify"):
                    config.set("verify_ssl", False)

                items = source_instance.search(keyword, limit=limit)
                all_items.extend(items)
                source_instance.close()
            except Exception as e:
                console.print(f"  [dim]Warning: Failed to search {source_name}: {e}[/dim]")
            finally:
                progress.update(task, completed=True)

    if not all_items:
        console.print(Panel(f"[yellow]No results found for '{keyword}'.[/yellow]",
                            title=f"Search: {keyword}"))
        return

    # Sort by score descending
    all_items.sort(key=lambda x: x.score, reverse=True)

    if output_format == "table":
        _display_items_table(all_items, title=f"Search Results for '{keyword}' ({len(all_items)} items)")
    else:
        try:
            formatter = get_formatter(output_format)
            formatted = formatter.format_items(all_items)

            if output:
                with open(output, "w", encoding="utf-8") as f:
                    f.write(formatted)
                console.print(f"[green]Output saved to:[/green] {output}")
            else:
                console.print(formatted)
        except ValueError as e:
            console.print(f"[red]Error:[/red] {e}")
            sys.exit(1)


@cli.command()
@click.pass_context
def sources(ctx: click.Context) -> None:
    """List all available data sources."""
    table = Table(
        title="Available Data Sources",
        box=box.ROUNDED,
        title_style="bold cyan",
        header_style="bold magenta",
    )

    table.add_column("Name", style="bold green", width=15)
    table.add_column("Source Type", style="yellow", width=15)
    table.add_column("Description", style="white")
    table.add_column("URL", style="dim blue")

    for name, cls in sorted(SOURCE_REGISTRY.items()):
        instance = cls()
        table.add_row(
            name,
            instance.source_type.value,
            instance.description,
            instance.base_url or "API",
        )
        instance.close()

    console.print(table)


@cli.command()
@click.argument("url")
@click.option("--format", "-f", "output_format", default="text",
              type=click.Choice(["text", "json", "markdown"]),
              help="Output format for extracted content")
@click.option("--output", "-o", default=None, help="Output file path (default: stdout)")
@click.pass_context
def fetch(ctx: click.Context, url: str, output_format: str, output: Optional[str]) -> None:
    """Extract content from a specific URL.

    URL: The URL to extract content from.
    """
    extractor = HTMLExtractor()

    # Apply CLI options
    config = extractor.config
    if ctx.obj.get("proxy"):
        config.set("proxy", ctx.obj["proxy"])
    if ctx.obj.get("no_cache"):
        config.set("cache_enabled", False)
    if ctx.obj.get("no_ssl_verify"):
        config.set("verify_ssl", False)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task(f"Fetching {url}...", total=None)
        try:
            result = extractor.extract(url)
        except Exception as e:
            progress.stop()
            console.print(f"[red]Error fetching URL:[/red] {e}")
            sys.exit(1)
        finally:
            progress.update(task, completed=True)

    if not result:
        console.print(Panel(f"[red]Failed to extract content from:[/red] {url}",
                            title="Extraction Failed"))
        return

    if output_format == "text":
        # Display extracted content
        console.print(Panel(
            f"[bold cyan]{result.title}[/bold cyan]\n\n"
            f"[dim]Author:[/dim] {result.author or 'N/A'}\n"
            f"[dim]Published:[/dim] {result.published_at or 'N/A'}\n"
            f"[dim]URL:[/dim] {result.url}\n"
            f"[dim]Words:[/dim] {result.metadata.get('word_count', 0)} | "
            f"[dim]Links:[/dim] {result.metadata.get('link_count', 0)} | "
            f"[dim]Images:[/dim] {result.metadata.get('image_count', 0)}",
            title="Extracted Content",
        ))

        if result.content:
            console.print()
            # Truncate very long content for terminal display
            content = result.content[:3000]
            if len(result.content) > 3000:
                content += f"\n\n[... truncated, {len(result.content)} chars total ...]"
            console.print(content)
    elif output_format == "json":
        import json
        formatted = json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(formatted)
            console.print(f"[green]Output saved to:[/green] {output}")
        else:
            console.print(formatted)
    elif output_format == "markdown":
        lines = [
            f"# {result.title}",
            "",
            f"**URL:** {result.url}",
            f"**Author:** {result.author or 'N/A'}",
            f"**Published:** {result.published_at or 'N/A'}",
            "",
            result.content or "No content extracted.",
        ]
        formatted = "\n".join(lines)
        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(formatted)
            console.print(f"[green]Output saved to:[/green] {output}")
        else:
            console.print(formatted)


def main() -> None:
    """Entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
