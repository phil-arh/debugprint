import sys
import os
from unittest.mock import MagicMock

import pytest

from debugprint import Debug


def stub_out_stderr(monkeypatch):
    mock_stderr = MagicMock()
    monkeypatch.setattr(sys.stderr, "write", mock_stderr)
    return mock_stderr


def test_possible_module_names():
    allowed_names = ["a", "a:b", "a_1:b_2", "Aa1:2_3"]
    for s in allowed_names:
        Debug(s)
    type_errors = [1, None]
    for s in type_errors:
        with pytest.raises(TypeError) as error:
            Debug(s)
    value_errors = ["", "£", "$", "a b", "*", "a:*"]
    for s in value_errors:
        with pytest.raises(ValueError) as error:
            Debug(s)


def test_with_no_debug_env(monkeypatch):
    os.environ["DEBUG"] = ""
    names = ["a", "a:b"]
    for s in names:
        mock_stderr = stub_out_stderr(monkeypatch)
        Debug(s)(1)
        mock_stderr.assert_not_called()


def test_with_asterisk(monkeypatch):
    os.environ["DEBUG"] = "*"
    test_strings = ["a", "a:b"]
    for s in test_strings:
        mock_stderr = stub_out_stderr(monkeypatch)
        Debug(s)(1)
        mock_stderr.assert_called_once()


def test_with_asterisk_at_end(monkeypatch):
    os.environ["DEBUG"] = "a:b:*"
    test_strings = ["a", "a:b"]
    for s in test_strings:
        mock_stderr = stub_out_stderr(monkeypatch)
        Debug(s)(1)
        mock_stderr.assert_not_called()
    test_strings = ["a:b:c", "a:b:c:d"]
    for s in test_strings:
        mock_stderr = stub_out_stderr(monkeypatch)
        Debug(s)(1)
        mock_stderr.assert_called_once()


def test_with_asterisk_in_the_middle(monkeypatch):
    os.environ["DEBUG"] = "a:*:c"
    test_strings = ["a", "a:b", "a:a:d", "a:b:d"]
    for s in test_strings:
        mock_stderr = stub_out_stderr(monkeypatch)
        Debug(s)(1)
        mock_stderr.assert_not_called()
    test_strings = ["a:b:c", "a:b:c:d", "a:a:c", "a:a:c:d"]
    for s in test_strings:
        mock_stderr = stub_out_stderr(monkeypatch)
        Debug(s)(1)
        mock_stderr.assert_called_once()


def test_with_minus_in_the_middle(monkeypatch):
    os.environ["DEBUG"] = "a:-b:c"
    test_strings = ["a", "a:b", "a:b:c", "a:a:d"]
    for s in test_strings:
        mock_stderr = stub_out_stderr(monkeypatch)
        Debug(s)(1)
        mock_stderr.assert_not_called()
    test_strings = ["a:c:c", "a:a:c", "a:f:c", "a:a:c"]
    for s in test_strings:
        mock_stderr = stub_out_stderr(monkeypatch)
        Debug(s)(1)
        mock_stderr.assert_called_once()
