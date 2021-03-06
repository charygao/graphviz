# lang.py - dot language creation helpers

"""Quote strings to be valid DOT identifiers, assemble attribute lists."""

import re

from . import tools

__all__ = ['quote', 'quote_edge', 'a_list', 'attr_list']

# http://www.graphviz.org/doc/info/lang.html

ID = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*|-?(\.\d+|\d+(\.\d*)?))$')

KEYWORD = re.compile(r'((node)|(edge)|(graph)|(digraph)|(subgraph)|(strict))$', re.IGNORECASE)

HTML_STRING = re.compile(r'<.*>$', re.DOTALL)

COMPASS = re.compile(r'((n)|(ne)|(e)|(se)|(s)|(sw)|(w)|(nw)|(c)|(_))$')


def quote(identifier,
          valid_id=ID.match, dot_keyword=KEYWORD.match, html=HTML_STRING.match):
    """Return DOT identifier from string, quote if needed.

    >>> quote('')
    '""'

    >>> quote('spam')
    'spam'

    >>> quote('spam spam')
    '"spam spam"'

    >>> quote('-4.2')
    '-4.2'

    >>> quote('.42')
    '.42'

    >>> quote('<<b>spam</b>>')
    '<<b>spam</b>>'
    """
    if html(identifier):
        pass
    elif not valid_id(identifier) or dot_keyword(identifier):
        return '"%s"' % identifier.replace('"', '\\"')
    return identifier


def quote_edge(identifier):
    """Return DOT edge statement node_id from string, quote if needed.

    >>> quote_edge('spam')
    'spam'

    >>> quote_edge('spam spam:eggs eggs')
    '"spam spam":"eggs eggs"'

    >>> quote_edge('spam:eggs:s')
    'spam:eggs:s'
    """
    node, _, rest = identifier.partition(':')
    parts = [quote(node)]
    if rest:
        port, _, compass = rest.partition(':')
        parts.append(quote(port))
        if compass:
            parts.append(compass)
    return ':'.join(parts)


def a_list(label=None, kwargs=None, attributes=None):
    """Return assembled DOT a_list string.

    >>> a_list('spam', {'spam': None, 'ham': 'ham ham', 'eggs': ''})
    'label=spam eggs="" ham="ham ham"'
    """
    result = ['label=%s' % quote(label)] if label is not None else []
    if kwargs:
        items = ['%s=%s' % (quote(k), quote(v))
            for k, v in tools.mapping_items(kwargs) if v is not None]
        result.extend(items)
    if attributes:
        if hasattr(attributes, 'items'):
            attributes = tools.mapping_items(attributes)
        items = ['%s=%s' % (quote(k), quote(v))
            for k, v in attributes if v is not None]
        result.extend(items)
    return ' '.join(result)


def attr_list(label=None, kwargs=None, attributes=None):
    """Return assembled DOT attribute list string.

    Sorts kwargs and attributes if they are plain dicts (to avoid
    unpredictable order from hash randomization in Python 3 versions).

    >>> attr_list()
    ''

    >>> attr_list('spam spam', kwargs={'eggs': 'eggs', 'ham': 'ham ham'})
    ' [label="spam spam" eggs=eggs ham="ham ham"]'

    >>> attr_list(kwargs={'spam': None, 'eggs': ''})
    ' [eggs=""]'
    """
    content = a_list(label, kwargs, attributes)
    if not content:
        return ''
    return ' [%s]' % content
