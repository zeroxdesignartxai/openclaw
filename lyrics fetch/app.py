import sys

from safe_lyrics.cli import main as cli_main
from safe_lyrics.web import run_server


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        raise SystemExit(run_server())

    raise SystemExit(cli_main())
