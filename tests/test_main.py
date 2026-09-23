from __future__ import annotations

import pytest

from studylog import __version__
from studylog.__main__ import main


def test_version_flag_prints_version_and_exits(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    assert __version__ in capsys.readouterr().out
