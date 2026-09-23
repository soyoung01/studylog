from __future__ import annotations

import os

from dotenv import load_dotenv

from .app import create_app


def main() -> None:
    load_dotenv()
    port = int(os.getenv("STUDYLOG_PORT", "5000"))
    app = create_app()
    print(f"Studylog 실행 중: http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=True)


if __name__ == "__main__":
    main()
