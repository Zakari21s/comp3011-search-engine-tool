"""Application entrypoint for the search engine CLI."""

from __future__ import annotations

from cli import parse_args


def run() -> int:
    """Run the CLI command dispatcher."""
    args = parse_args()

    # TODO: Wire command handlers to crawler/parser/indexer/storage/search modules.
    # TODO: Return non-zero exit codes for recoverable user-facing errors.
    print(f"Command '{args.command}' is scaffolded but not implemented yet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())

