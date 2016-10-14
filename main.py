"""Provides a command line interface to build abstractions of CSS files.
   Can output a complete representation of a file, or test intersection of individual selector pairs.
   If a file is provided, the abstraction is output.
   If no file is provided, selectors are read from STDIN in pairs, and E output if the intersection is empty (else N).

Usage:
  main.py [-p] [<file>]
  main.py (-h | --help)
  main.py --version

Options:
  -p --multi-props          Combines multiply defined properties into a single value (e.g. { background: red; background: white } becomes { background: red;white }
  --version                 Show the version.
"""

import sys

from docopt import docopt, DocoptExit

import simplecssbuilder
import cssfile

def emptiness_mode():
    """Runs in a loop, reading two selectors from stdin (on two lines), and
    writing E to stdout if the selectors do not overlap, N otherwise"""

    while True:
        try:
            sel1 = sys.stdin.readline()
            if sel1 == "":
                break
            sel2 = sys.stdin.readline()
            if sel2 == "":
                break
            if simplecssbuilder.selectors_overlap_str(sel1, sel2):
                sys.stdout.write("N")
            else:
                sys.stdout.write("E")
        except EOFError:
            break

def build_mode():
    """Reads a file and outputs simpleCSS Model"""
    css = cssfile.fromfile(arguments['<file>'],
                           arguments['--multi-props'])
    print str(css)


if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding("utf-8")
    arguments = docopt(__doc__, version='v0.1')

    if arguments['<file>'] is None:
        emptiness_mode()
    else:
        build_mode()
