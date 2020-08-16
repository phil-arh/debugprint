import sys
import os
from unittest.mock import MagicMock

from src.debugprint import Debug

os.environ["DEBUG"] = "*"


def test_basic_printing(monkeypatch):
    mock_stderr = MagicMock()
    monkeypatch.setattr(sys.stderr, "write", mock_stderr)
    debug = Debug("a:b:c")
    debug(10)
    print("args:")
    print(mock_stderr.call_args)
