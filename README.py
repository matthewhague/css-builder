# CSS Builder

A tool/library for building an abstract representation of a CSS file as a set of
pairs (selector, declaration) with an ordering (representing the order selectors
must appear in the CSS file to maintain the overriding semantics).  Can
also be used to test whether two selectors may match the same node in some DOM.

## Requirements:

(Possibly a superset)

* [docopt 0.6.2](https://pypi.python.org/pypi/docopt)
* [enum34](https://pypi.python.org/pypi/enum34)
* [lxml 3.4.4](https://pypi.python.org/pypi/lxml)
* [tinycss 0.3](https://pypi.python.org/pypi/tinycss)
* [z3](http://research.microsoft.com/en-us/um/redmond/projects/z3/z3.html)

Borrowed and modified code from

* [cssselect 0.9.1](https://pypi.python.org/pypi/cssselect)

## Running

    python main.py --help

where "python" is your python 2.7 command.
