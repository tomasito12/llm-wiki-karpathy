"""CLI entry point for the management web backend."""

from __future__ import annotations

import argparse
from pathlib import Path

import uvicorn

from src.management_web.api import create_app
from src.wiki_paths.cli_helpers import add_paths_config_argument


def build_parser() -> argparse.ArgumentParser:
    """Build the management API CLI parser.

    Returns:
        Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="management-api",
        description="Run the LLM Wiki management web backend.",
    )
    add_paths_config_argument(parser)
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind.")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind.")
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable uvicorn reload for local development.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the management API server.

    Args:
        argv: Optional CLI arguments.

    Returns:
        Process exit code.
    """
    args = build_parser().parse_args(argv)
    paths_config: Path | None = args.paths_config
    app = create_app(paths_config=paths_config)
    uvicorn.run(app, host=args.host, port=args.port, reload=args.reload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
