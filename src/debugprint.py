"""Debug print module like node.js debug."""
import sys
import os
import time
import random
from pprint import pformat
from xml.etree import ElementTree
from xml.dom import minidom

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
        if not self._should_print():
            return
        global _time_debug_last_called
        time_now = int(time.time() * 1000)
        _time_debug_last_called = time_now
        if caption:
            caption = f"<< {caption} >>"  # replace with French quote marks
        for format_function in _format_functions:
            try:
                response = format_function(printable)
            except:  # pylint: disable=bare-except
                response = None
            if response:
                break
        if response:
            printable = f">>>>\n{response}\n<<<<"
        elif isinstance(printable, (list, dict, set)):
            printable = f">>>>\n{pformat(printable)}\n<<<<"
        elif isinstance(printable, ElementTree.ElementTree):
            formatted_printable = minidom.parseString(
                ElementTree.tostring(printable)
            ).toprettyxml()
        elif not isinstance(printable, str):
            printable = repr(printable)
        sys.stderr.write(
            f"{_BOLD}{self.ansi_colour}{self.module_name} {_NO_FORMAT}"
            f"{_BOLD}{caption}{_NO_FORMAT}"
            f"{printable}"
            f"{_TIME_PRINT_COLOUR} +{time_since_last_called}"
            f"{_NO_FORMAT}\n"
        )

    def _should_print(self):
        if not "DEBUG" in os.environ:
            return False
        if os.environ["DEBUG"] == "*":
            return True
        split_debug = os.environ["DEBUG"].split(":")
        for matched in zip(split_debug, self.split_module_name):
            if matched[0] == "*":
                continue
            if matched[0] != matched[1]:
                break
        else:  # nobreak
            return True
        return False
