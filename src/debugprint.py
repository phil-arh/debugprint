"""Debug print module like node.js debug."""
import sys
import os
import time
import random
import re
from pprint import pformat
from xml.etree import ElementTree
from xml.dom import minidom

module_name_re = re.compile(r"^[A-Za-z0-9:_]+$")


def _ansify_colour(colour_code):
    return f"\x1b[38;5;{colour_code}m"


_NO_FORMAT = "\033[0m"
_BOLD = "\033[1m"
_GREY = _ansify_colour(243)
_ORANGE = _ansify_colour(202)
_GREEN = _ansify_colour(34)
_RED = _ansify_colour(9)
_TIME_PRINT_COLOUR = _ansify_colour(88)

_format_functions = []


def use_format(format_function):
    global _format_functions
    _format_functions.append(format_function)


_debug_colours_already_used = []
_time_debug_last_called = int(time.time() * 1000)


class Debug:  # pylint: disable=too-few-public-methods
    """Class that emulates the behaviour of the node.js debug module."""

    def __init__(self, module_name):
        if not isinstance(module_name, str):
            raise TypeError(f"module name must be a string not {type(module_name)}")
        if not module_name_re.match(module_name):
            raise ValueError(
                "module name must consist of letters, numbers, underscores, "
                "and colons only, e.g. 'app', 'app:main', app:some_library' - "
                f"<{module_name}> is invalid"
            )
        self.module_name = module_name
        self.split_module_name = module_name.split(":")
        global _debug_colours_already_used
        for i in range(227 - 22):  # pylint: disable=unused-variable
            new_text_colour = random.randrange(22, 227)
            if new_text_colour not in _debug_colours_already_used:
                self.text_colour = new_text_colour
                self.ansi_colour = _ansify_colour(self.text_colour)
                break
        else:
            _debug_colours_already_used = []

    def __call__(self, printable, caption=""):
        if not self.enabled:
            return
        global _time_debug_last_called
        time_now = int(time.time() * 1000)
        time_since_last_called = time_now - _time_debug_last_called
        _time_debug_last_called = time_now
        if caption:
            caption = f"« {caption} » "
        response = None
        for format_function in _format_functions:
            try:
                response = format_function(printable)
            except:  # pylint: disable=bare-except
                response = None
            if response:
                break
        if response:
            formatted_printable = f">>>>\n{response}\n<<<<"
        elif isinstance(printable, (list, dict, set, tuple)):
            formatted_printable = f">>>>\n{pformat(printable)}\n<<<<"
        elif isinstance(printable, (ElementTree.ElementTree, ElementTree.Element)):
            beautified_xml = minidom.parseString(
                ElementTree.tostring(printable)
            ).toprettyxml()
            formatted_printable = f">>>>\n{beautified_xml}\n<<<<"
        elif not isinstance(printable, str):
            formatted_printable = repr(printable)
        sys.stderr.write(
            f"{_BOLD}{self.ansi_colour}{self.module_name} {_NO_FORMAT}"
            f"{_BOLD}{caption}{_NO_FORMAT}"
            f"{formatted_printable}"
            f"{_TIME_PRINT_COLOUR} +{time_since_last_called}"
            f"{_NO_FORMAT}\n"
        )

    @property
    def enabled(self):
        if not "DEBUG" in os.environ or not os.environ["DEBUG"]:
            return False
        if os.environ["DEBUG"] == "*":
            return True
        split_debug = os.environ["DEBUG"].split(":")
        if len(split_debug) > len(self.split_module_name):
            return False
        for debug_path, module_path in zip(split_debug, self.split_module_name):
            if debug_path == "*":
                continue
            if len(debug_path) > 1 and debug_path[0] == "-":
                if debug_path[1:] == module_path:
                    break
                continue
            if debug_path != module_path:
                break
        else:  # nobreak
            return True
        return False
