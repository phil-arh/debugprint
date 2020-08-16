import sys
import os
import re
import xml
from unittest.mock import MagicMock

from debugprint import Debug

os.environ["DEBUG"] = "*"

colour_re = re.compile(r".\[38;5;\d+m")
ms_re = re.compile(r"\+\d+")


def remove_custom_colour_and_ms(string_with_colour):
    print(colour_re.search(string_with_colour))
    return ms_re.sub("", colour_re.sub("", string_with_colour, count=1))


def test_basic_printing(monkeypatch):
    # GIVEN
    mock_stderr = MagicMock()
    monkeypatch.setattr(sys.stderr, "write", mock_stderr)
    debug = Debug("a:b:c")
    # WHEN
    debug(10)
    # THEN
    assert remove_custom_colour_and_ms(
        mock_stderr.call_args[0][0]
    ) == remove_custom_colour_and_ms(
        "\x1b[1m\x1b[38;5;117ma:b:c \x1b[0m\x1b[1m\x1b[0m10\x1b[38;5;88m +2\x1b[0m\n"
    )


def test_printing_with_caption(monkeypatch):
    # GIVEN
    mock_stderr = MagicMock()
    monkeypatch.setattr(sys.stderr, "write", mock_stderr)
    debug = Debug("a:b:c")
    # WHEN
    debug(10, "a caption")
    # THEN
    assert remove_custom_colour_and_ms(
        mock_stderr.call_args[0][0]
    ) == remove_custom_colour_and_ms(
        "\x1b[1m\x1b[38;5;79ma:b:c \x1b[0m\x1b[1m« a caption » \x1b[0m10\x1b[38;5;88m \x1b[0m\n"
    )


def test_dict_printing(monkeypatch):
    # GIVEN
    mock_stderr = MagicMock()
    monkeypatch.setattr(sys.stderr, "write", mock_stderr)
    output_dict = {
        "glossary": {
            "title": "example glossary",
            "GlossEntry": {
                "ID": "SGML",
                "SortAs": "SGML",
                "GlossTerm": "Standard Generalized Markup Language",
                "Acronym": "SGML",
                "Abbrev": "ISO 8879:1986",
                "GlossDef": {
                    "para": "A meta-markup language, used to create markup languages such as DocBook.",
                    "GlossSeeAlso": ["GML", "XML"],
                },
                "GlossSee": "markup",
            },
        }
    }
    debug = Debug("a:b:c")
    # WHEN
    debug(output_dict)
    # THEN
    expected = "\x1b[1m\x1b[38;5;168ma:b:c \x1b[0m\x1b[1m\x1b[0m>>>>\n{'glossary': {'GlossEntry': {'Abbrev': 'ISO 8879:1986',\n                             'Acronym': 'SGML',\n                             'GlossDef': {'GlossSeeAlso': ['GML', 'XML'],\n                                          'para': 'A meta-markup language, '\n                                                  'used to create markup '\n                                                  'languages such as DocBook.'},\n                             'GlossSee': 'markup',\n                             'GlossTerm': 'Standard Generalized Markup '\n                                          'Language',\n                             'ID': 'SGML',\n                             'SortAs': 'SGML'},\n              'title': 'example glossary'}}\n<<<<\x1b[38;5;88m +17\x1b[0m\n"
    assert remove_custom_colour_and_ms(
        mock_stderr.call_args[0][0]
    ) == remove_custom_colour_and_ms(expected)


def test_xml_printing(monkeypatch):
    # GIVEN
    mock_stderr = MagicMock()
    monkeypatch.setattr(sys.stderr, "write", mock_stderr)
    debug = Debug("a:b:c")
    xml_output = xml.etree.ElementTree.fromstring(
        """ <glossary><title>example glossary</title><GlossDiv><title>S</title><GlossList><GlossEntry ID="SGML" SortAs="SGML"><GlossTerm>Standard Generalized Markup Language</GlossTerm> <Acronym>SGML</Acronym><Abbrev>ISO 8879:1986</Abbrev><GlossDef><para>A meta-markup language, used to create markup languages such as DocBook.</para><GlossSeeAlso OtherTerm="GML" /><GlossSeeAlso OtherTerm="XML" /> </GlossDef> <GlossSee OtherTerm="markup" /></GlossEntry></GlossList></GlossDiv></glossary>
     """
    )
    # WHEN
    debug(xml_output)
    # THEN
    assert remove_custom_colour_and_ms(
        mock_stderr.call_args[0][0]
    ) == remove_custom_colour_and_ms(
        '\x1b[1m\x1b[38;5;134ma:b:c \x1b[0m\x1b[1m\x1b[0m>>>>\n<?xml version="1.0" ?>\n<glossary>\n\t<title>example glossary</title>\n\t<GlossDiv>\n\t\t<title>S</title>\n\t\t<GlossList>\n\t\t\t<GlossEntry ID="SGML" SortAs="SGML">\n\t\t\t\t<GlossTerm>Standard Generalized Markup Language</GlossTerm>\n\t\t\t\t \n\t\t\t\t<Acronym>SGML</Acronym>\n\t\t\t\t<Abbrev>ISO 8879:1986</Abbrev>\n\t\t\t\t<GlossDef>\n\t\t\t\t\t<para>A meta-markup language, used to create markup languages such as DocBook.</para>\n\t\t\t\t\t<GlossSeeAlso OtherTerm="GML"/>\n\t\t\t\t\t<GlossSeeAlso OtherTerm="XML"/>\n\t\t\t\t\t \n\t\t\t\t</GlossDef>\n\t\t\t\t \n\t\t\t\t<GlossSee OtherTerm="markup"/>\n\t\t\t</GlossEntry>\n\t\t</GlossList>\n\t</GlossDiv>\n</glossary>\n\n<<<<\x1b[38;5;88m +3\x1b[0m\n'
    )
