import json
from dataclasses import asdict
from typing import Annotated, Optional

import typer

from boj_stat_search.api import BojApiError, get_data_code, get_data_layer, get_metadata
from boj_stat_search.catalog import generate_metadata_parquet_files
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


@app.command("generate-metadata-parquet")
def generate_metadata_parquet_cmd(
    output_dir: Annotated[
        str,
        typer.Option(
            "--output-dir",
            "-o",
            help="Directory where per-DB metadata Parquet files will be written",
        ),
    ] = "metadata",
    db: Annotated[
        Optional[list[str]],
        typer.Option(
            "--db",
            help="Database code to export (repeat option to select multiple DBs)",
        ),
    ] = None,
    min_request_interval: Annotated[
        float,
        typer.Option(
            "--min-request-interval",
            help="Minimum delay in seconds between BOJ API requests",
        ),
    ] = 1.0,
) -> None:
    """Generate per-DB metadata Parquet files."""
    report = generate_metadata_parquet_files(
        output_dir=output_dir,
        dbs=db,
        min_request_interval=min_request_interval,
        show_progress=True,
    )

    for db_name in report.succeeded_dbs:
        row_count = report.row_counts[db_name]
        typer.echo(f"{db_name}: wrote {row_count} rows")

    if report.failed_count > 0:
        typer.echo(
            f"Metadata Parquet export completed with failures "
            f"({report.succeeded_count}/{report.total_dbs} succeeded).",
            err=True,
        )
        for db_name in report.failed_dbs:
            message = report.error_messages[db_name]
            typer.echo(f"{db_name}: {message}", err=True)
        raise typer.Exit(code=1)

    typer.echo(
        f"Metadata Parquet export completed successfully "
        f"({report.succeeded_count}/{report.total_dbs} succeeded)."
    )


if __name__ == "__main__":
    app()
