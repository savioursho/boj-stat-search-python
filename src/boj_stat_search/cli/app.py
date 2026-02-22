import json
from dataclasses import asdict
from typing import Annotated, Optional

import typer

from boj_stat_search.api import BojApiError, get_data_code, get_data_layer, get_metadata
from boj_stat_search.core import list_db
from boj_stat_search.display import show_layers

app = typer.Typer(
    help="Query Bank of Japan Time Series Statistical Data from the terminal."
)


@app.command("list-db")
def list_db_cmd() -> None:
    """List all available databases."""
    databases = list_db()

    name_width = max(len(db.name) for db in databases)
    cat_width = max(len(db.category) for db in databases)

    for db in databases:
        typer.echo(f"{db.name:<{name_width}}  {db.category:<{cat_width}}  {db.desc}")


@app.command("get-metadata")
def get_metadata_cmd(
    db: Annotated[str, typer.Argument(help="Database code (e.g. FM01)")],
) -> None:
    """Get metadata for a database and print as JSON."""
    try:
        result = get_metadata(db)
    except BojApiError as exc:
        typer.echo(f"API error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(json.dumps(asdict(result), ensure_ascii=False, indent=2))


@app.command("show-layers")
def show_layers_cmd(
    db: Annotated[str, typer.Argument(help="Database code (e.g. FM01)")],
    layer: Annotated[
        Optional[str],
        typer.Option(
            "--layer", "-l", help="Filter to a specific layer (e.g. '1' or '1,2')"
        ),
    ] = None,
) -> None:
    """Show the layer structure of a database."""
    try:
        result = get_metadata(db)
    except BojApiError as exc:
        typer.echo(f"API error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    show_layers(result.result_set, layer)


@app.command("get-data-code")
def get_data_code_cmd(
    db: Annotated[str, typer.Argument(help="Database code (e.g. FM01)")],
    code: Annotated[str, typer.Argument(help="Series code (e.g. FM01'STRDCLUCON)")],
    start_date: Annotated[
        Optional[str],
        typer.Option("--start-date", "-s", help="Start date (YYYY or YYYYMM)"),
    ] = None,
    end_date: Annotated[
        Optional[str],
        typer.Option("--end-date", "-e", help="End date (YYYY or YYYYMM)"),
    ] = None,
    start_position: Annotated[
        Optional[int],
        typer.Option("--start-position", "-p", help="Start position for pagination"),
    ] = None,
) -> None:
    """Get data by series code and print as JSON."""
    try:
        result = get_data_code(
            db=db,
            code=code,
            start_date=start_date,
            end_date=end_date,
            start_position=start_position,
        )
    except BojApiError as exc:
        typer.echo(f"API error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(json.dumps(asdict(result), ensure_ascii=False, indent=2))


@app.command("get-data-layer")
def get_data_layer_cmd(
    db: Annotated[str, typer.Argument(help="Database code (e.g. FM01)")],
    frequency: Annotated[str, typer.Argument(help="Frequency (e.g. D, M, Q)")],
    layer: Annotated[str, typer.Argument(help="Layer specification (e.g. '1,*')")],
    start_date: Annotated[
        Optional[str],
        typer.Option("--start-date", "-s", help="Start date (YYYY or YYYYMM)"),
    ] = None,
    end_date: Annotated[
        Optional[str],
        typer.Option("--end-date", "-e", help="End date (YYYY or YYYYMM)"),
    ] = None,
    start_position: Annotated[
        Optional[int],
        typer.Option("--start-position", "-p", help="Start position for pagination"),
    ] = None,
) -> None:
    """Get data by layer and print as JSON."""
    try:
        result = get_data_layer(
            db=db,
            frequency=frequency,
            layer=layer,
            start_date=start_date,
            end_date=end_date,
            start_position=start_position,
        )
    except BojApiError as exc:
        typer.echo(f"API error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(json.dumps(asdict(result), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    app()
