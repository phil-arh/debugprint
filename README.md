# debugprint

*A light zero-dependency module for nicely printing things for debugging*

`debugprint` is a slightly more featureful Python clone of the node.js `debug` module. It behaves almost exactly as node.js debug does, with the following exceptions:

 - Python imports behave differently from node.js `require` so `debug` instances are created differently
 - You can define custom format functions in debugprint
 - You can add captions to print-outs in debugprint
 - In node.js debug, you can change the enabled namespace within a module by doing `debug.disable()` or `debug.enable('some:namespaces:*')`

Otherwise, the usage is pretty much exactly the same - make a new `Debug` instance for each module, and run the program with the `DEBUG` environment variable set to something sensible (details on setting `DEBUG` are below).

Why use `debugprint` instead of just regular `print`?

 - Prints only when the `DEBUG` environment variable is set to a matching value (more on this below) so you don't need to spend time finding and removing print statements prior to releasing for production
 - Prints to `stderr` not `stdout` - much better for command line tools as it doesn't interfere with piping the data on to other programs
 - Provides the name of the module the statement is being output from - module name is also colour-coded
 - Allows passing an optional caption
 - Automatically pretty-prints built-in collection types
 - Allows adding custom format functions to pretty-print custom data types like `lxml` trees or `pyrsistent` immutable data structures.

## Example print-outs

### Scalar values

`debug("Hello, world!")` and `debug("Hello, world!", "a caption")`:

![Basic](https://github.com/phil-arh/debugprint/blob/master/screenshots/basic.png)

### Dicts

`debug(example_dict)`

![Dict no caption](https://github.com/phil-arh/debugprint/blob/master/screenshots/dict_no_caption.png)

`debug(example_dict, "A pretty-printed nested dict")`

![Dict with caption](https://github.com/phil-arh/debugprint/blob/master/screenshots/dict_caption.png)

### XML

`debug(example_xml)`

![XML](https://github.com/phil-arh/debugprint/blob/master/screenshots/xml.png)

**`debugprint` can also pretty-print nested lists, tuples, and mixed JSON by default - essentially anything that can be handled by the standard library `pprint` module.**

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

In order to get `debugprint` to print, you need to run your module/script/application with the `DEBUG` environment variable set.

There are two ways to do this in bash:

```bash
# setting the DEBUG environment variable to "*" as an example

$ DEBUG="*" python3 myscript.py

# or

$ export DEBUG="*"
$ python3 myscript.py
```

Setting `DEBUG` to `*` tells `debugprint` to always print. Occasionally that's the behaviour you want, but more likely you'll want to restrict it to a limited subset of possible `debug()` calls. You can therefore set it to colon-separated paths, like the following examples:

 - `app` - `debug()` calls will only print in this scenario: `debug = Debug("app")`
 - `app:thing` will only print for `debug = Debug(app:thing)`
 - `app:*` - will print if `debug = Debug("app")` or `debug = Debug(app:thing)` or `debug = Debug(app:thing:anotherthing)` etc.
 - `app:*:anotherthing` will print if `debug = Debug("app:thing:anotherthing")` or `debug = Debug("app:somethingelse:anotherthing")` etc.

You can also set `DEBUG` so multiple different paths are enabled. For instance:

 - `app,app:thing` - `debug()` calls will print where `debug = Debug("app")` or `debug = Debug("app:thing")`
 - `app:thing,app:anotherthing` - will print where `debug = Debug("app:thing")` or `debug = Debug("app:anotherthing")`

This should hopefully be fairly intuitive. Just set the path of the `DEBUG` environment variable to match what you want to print. You'll usually be fine with setting it to `DEBUG=nameofmyapp,nameofmyapp:*` and leaving it, but if you're working on a big codebase or trying to figure out a particularly persistent bug, you may want to adjust it to narrow down what gets printed.

## Custom format functions

By default, `debugprint` will attempt to pretty-print `list`s, `dict`s, `set`s, `tuple`s, and `xml.etree.ElementTree.ElementTree`s. But what if you're using non-standard data structures, like `lxml` trees or `pyrsistent` immutable data structures?

You can define custom format functions for any data type you like. The general structure of a custom format function is that it returns either a string to be printed or `None`. `debugprint` will call each defined custom format function in turn. The logic in `debugprint` is similar to this:

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

from lxml import etree
from pyrsistent import PRecord, PMap, PVector, PSet, thaw

import debugprint


# a custom format function for LXML element trees
def lxml_formatter(possible_lxml_object):
    if isinstance(possible_lxml_object, etree._Element):
        return etree.tostring(
            possible_lxml_object,
            pretty_print=True,
            encoding="unicode",
        )
    else:
        return None

# a custom format function for pyrsistent immutable data structures
def pyrsistent_formatter(possible_pyrsistent_data_structure):
    if isinstance(possible_pyrsistent_data_structure, (PRecord, PMap, PVector, PSet)):
        return pformat(thaw(possible_pyrsistent_data_structure))
    else:
        return None

debugprint.use_format(lxml_formatter)
debugprint.use_format(pyrsistent_formatter)
```

The basic logic of a custom format function is just:

```python
def custom_format_function(some_input):
    if isinstance(some_input, the_type_this_function_is_looking_for):
        return format_this_special_type_for_printing(some_input)
    else:
        # you can return any falsy value here
        return None
```
