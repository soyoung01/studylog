from __future__ import annotations

import argparse
import os
from collections.abc import Sequence

from dotenv import load_dotenv

from . import __version__
from .app import create_app


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="studylog")
    parser.add_argument("--version", action="version", version=f"studylog {__version__}")
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    build_parser().parse_args(argv)
    load_dotenv()
    port = int(os.getenv("STUDYLOG_PORT", "5000"))
    app = create_app()
    print(f"Studylog 실행 중: http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=True)


if __name__ == "__main__":
    main()
