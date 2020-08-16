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
    return "\x1b[38;5;{}m".format(colour_code)


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
            raise TypeError(
                "module name must be a string not {}".format(type(module_name))
            )
        if not module_name_re.match(module_name):
            raise ValueError(
                (
                    "module name must consist of letters, numbers, underscores, "
                    "and colons only, e.g. 'app', 'app:main', app:some_library' - "
                    "<{}> is invalid"
                ).format(module_name)
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
            caption = "« {} » ".format(caption)
        response = None
        for format_function in _format_functions:
            try:
                response = format_function(printable)
            except:  # pylint: disable=bare-except
                response = None
            if response:
                break
        if response:
            formatted_printable = ">>>>\n{}\n<<<<".format(response)
        elif isinstance(printable, (list, dict, set, tuple)):
            formatted_printable = ">>>>\n{}\n<<<<".format(pformat(printable))
        elif isinstance(printable, (ElementTree.ElementTree, ElementTree.Element)):
            beautified_xml = minidom.parseString(
                ElementTree.tostring(printable)
            ).toprettyxml()
            formatted_printable = ">>>>\n{}\n<<<<".format(beautified_xml)
        elif not isinstance(printable, str):
            formatted_printable = repr(printable)
        sys.stderr.write(
            (
                "{bold}{ansi_colour}{module_name} {no_format}"
                "{bold}{caption}{no_format}"
                "{formatted_printable}"
                "{time_print_colour} +{time_since_last_called}"
                "{no_format}\n"
            ).format(
                bold=_BOLD,
                ansi_colour=self.ansi_colour,
                module_name=self.module_name,
                no_format=_NO_FORMAT,
                caption=caption,
                formatted_printable=formatted_printable,
                time_print_colour=_TIME_PRINT_COLOUR,
                time_since_last_called=time_since_last_called,
            )
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
