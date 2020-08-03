# debugprint

*A light zero-dependency module for nicely printing things for debugging*

`debugprint` is a slightly more featurefull Python clone of the node.js `debug` module. It behaves almost exactly as node.js debug does, apart from two things:

 - You can define custom format functions
 - You can add captions to print-outs

Otherwise, the usage is pretty much exactly the same - make a new `Debug` instance for each module, and run the program with the `DEBUG` environment variable set to something sensible (details on setting `DEBUG` are below).

Why use `debugprint` instead of just regular `print`?

 - Prints only when the `DEBUG` environment variable is set to a matching value (more on this below) so you don't need to spend time finding and removing print statements prior to releasing for production
 - Prints to `stderr` not `stdout` - much better for command line tools as it doesn't interfere with piping the data on
 - Provides the name of the module the statement is being output from - module name is also colour-coded
 - Allows passing an optional caption
 - Automatically pretty-prints built-in collection types
 - Allows adding custom format functions to pretty-print custom data types like `lxml` trees or `pyrsistent` immutable data structures.

## Installation

```bash
# via pip
pip install debugprint

# via pipenv
pipenv install debugprint

```

## Usage

Import into every module where you want to do debug printing, then create an instance of the `Debug` class for that module.

```python
from debugprint import Debug

debug = Debug("my_application:some_subpackage:this_module")

# simple printing
debug("some string value")
debug(123)
debug(False)

# pretty printing collections
debug([1, 2, 3])
debug({"a": 1, "b": 2, "c": 3})

# printing things with captions
debug(call_this_function_that_returns_a_bool(), "bool returned by this function")
debug(some_var, "the value of some_var at this point in the pipeline")

```

## Setting the `DEBUG` environment variable

By default, `debugprint` doesn't print anything. This is intentional - debug printouts are unnecessary in production and can be actively irritating to users - not to mention, depending on the situation, a potential security risk.

In order to get `debugprint` to print, you need to run it with the `DEBUG` environment variable set.

There are two ways to do this in bash:

```bash
DEBUG="*" python3 myscript.py

# or

export DEBUG="*"
python3 myscript.py
```

Setting `DEBUG` to `*` tells `debugprint` to always print. Occasionally that's the behaviour you want, but more likely you'll want to restrict it to a limited subset of possible `debug()` calls. You can therefore set it to colon-separated paths, like the following examples:

 - `app` - `debug()` calls will only print in this scenario: `debug = Debug("app")`
 - `app:thing` will only print for `debug = Debug(app:thing)`
 - `app:*` - will print if `debug = Debug("app")` or `debug = Debug(app:thing)` or `debug = Debug(app:thing:anotherthing)` etc.
 - `app:*:anotherthing` will print if `debug = Debug("app:thing:anotherthing")` or `debug = Debug("app:somethingelse:anotherthing")` etc.

This should hopefully be fairly intuitive. Just set the path of the `DEBUG` environment variable to match what you want to print. You'll usually be fine with setting it to `DEBUG=nameofmyapp:*` and leaving it, but if you're working on a big codebase or trying to figure out a particularly persistent bug, you may want to adjust it to narrow down what gets printed.

## Custom format functions

By default, `debugprint` will attempt to pretty-print `list`s, `dict`s, `set`s, `tuple`s, and `xml.etree.ElementTree.ElementTree`s. But what if you're using some kind of custom data structures, like `lxml` trees or `pyrsistent` immutable data structures?

You can define custom format functions for any data type you like. The general structure of a custom format function is that it returns either a string to be printed or `None`. `debugprint` will call each defined custom format function in turn. The logic is similar to this:

```python
# not the actual code but not far off
input_value # value to print
for function in custom_functions:
    output_string = function(input_value)
    if output_string:
        break
if output_string:
    # print this string
else:
    # carry on and try using the default formatters
```

### Example custom format functions

The best way to see what a custom format function looks like is to check out a couple of examples:

```python
from pprint import pformat

import debugprint

from lxml import etree
from pyrsistent import PRecord, PMap, PVector, PSet, thaw

# a custom format function for LXML element trees
def lxml_formatter(possible_lxml_object):
    if isinstance(lxml_object, etree._Element):
        return etree.tostring(
            possible_lxml_object, pretty_print=True, encoding="unicode"
        )
    return None

# a custom format function for pyrsistent immutable data structures
def pyrsistent_formatter(possible_pyrsistent_data_structure):
    if isinstance(possible_pyrsistent_data_structure, (PRecord, PMap, PVector, PSet)):
        return pformat(thaw(possible_pyrsistent_data_structure))
    return None

debugprint.use_format(lxml_formatter)
debugprint.use_format(pyrsistent_formatter)
```

The basic logic of a custom format function is just: if you can format the input, return that, otherwise, return `None` to tell `debugprint` to move on.
