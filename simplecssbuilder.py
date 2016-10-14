"""Functions for constructing from s CSSFile a simpleCSS object for minimisation
purposes"""

from itertools import combinations
from timeit import default_timer

import cssfile
from cssfile import CSSFile
from simpleCSS import *
import cssautomaton
import autemptiness
from cliqueCSS import *
import cssselect_parser

__DEBUG__ = True

numchecks = 0
numpositive = 0
numnontrivialchecks = 0
numpositivenontrivial = 0

def fromfile(filename):
    """Constructs a simpleCSS object from a given CSS file

    :param filename:
        The name as a string of the CSS file
    :returns:
        a simpleCSS object representing the file
    """
    css = cssfile.fromfile(filename)
    return fromcssfile(css)

def fromstring(css):
    """Constructs a simpleCSS object from a given CSS string

    :param css:
        The string representation of the CSS file
    :returns:
        a simpleCSS object representing the file
    """
    css = cssfile.fromstring(css)
    return fromcssfile(css)

def fromcssfile(css):
    """Constructs a simpleCSS object from a given CSSFile

    :param css:
        The CSSFile
    :returns:
        a simpleCSS object representing the file
    """
    # dict from (prop, selector, value) to simpleRule
    rules = {}
    prop_names = dict()

    for p in css.get_props():
        for spec in css.get_specificities(p):
            for (s, v) in css.get_values(p, spec):
                (l, unique) = css.get_info(p, spec, s, v)
                rules[(p, s, v)] = _make_simple_rule(p,
                                                     cssfile.selector_str(s),
                                                     v,
                                                     unique)
                prop_names[_make_prop(p, v)] = p

    reset_selectors_overlap_memo()
    order = set()

    for p in css.get_props():
        for spec in css.get_specificities(p):
            selvals = css.get_values(p, spec)
            num = len(selvals)
            for ((s1, v1),
                 (s2, v2)) in combinations(selvals, 2):
                if v1 != v2:
                    e1 = rules[(p, s1, v1)]
                    e2 = rules[(p, s2, v2)]
                    if selectors_overlap(s1, s2):
                        (l1, _) = css.get_info(p, spec, s1, v1)
                        (l2, _) = css.get_info(p, spec, s2, v2)
                        enew = (e1, e2)
                        if l2 < l1:
                            enew = (e2, e1)
                        order.add(enew)

    complex_rules = [ _make_rule(r) for r in css.get_rules() ]

    return simpleCSS(list(rules.values()),
                     list(order),
                     complex_rules,
                     prop_names = prop_names)



def _make_rule(r):
    """
    :param r:
        CSSRule
    :returns:
        a rule object from simpleCSS built from the given CSSRule
    """
    decls = [ p + ":" + v for (p, v) in r.get_declarations() ]
    sels = { cssfile.selector_str(s.parsed_tree) for s in r.get_selectors() }
    return rule(sels, decls)

def _make_simple_rule(prop, sel, value, unique = True):
    """
    :param prop:
        The property in same format as simpleRule
    :param sel:
        The selector in same format as simpleRule
    :param value:
        The value as a string
    :param unique:
        The simpleCSS rule only appears once in the file
    :returns:
        A simpleRule made from the arguments
    """
    return simpleRule(sel,
                      _make_prop(prop, value))

def _make_prop(prop, value):
    return prop + ":" + value

_selectors_overlap_memo = dict()
_selectors_automata = dict()

def reset_selectors_overlap_memo():
    """
    _selectors_overlap and _make_selector_automata are memoized to speed it up.
    Call this to reset.
    """
    global _selectors_overlap_memo
    global _selectors_automata
    _selectors_overlap_memo = dict()
    _selectors_automata = dict()

def selectors_overlap_str(css1, css2):
    """
    Note: is memoized, call reset_selectors_overlap_memo before using.

    :param css1:
        css selector as string
    :param css2:
        css selector as string
    :returns:
        True iff the two selectors may match the same node
    """
    pt1 = cssselect_parser.parse(css1).pop().parsed_tree
    pt2 = cssselect_parser.parse(css2).pop().parsed_tree
    return selectors_overlap(pt1, pt2)

def selectors_overlap(css1, css2):
    """
    Note: is memoized, call reset_selectors_overlap_memo before using.

    :param css1:
        css selector as cssselect parsed tree
    :param css2:
        css selector as cssselect parsed tree
    :returns:
        True iff the two selectors may match the same node
    """
    global numchecks
    global numpositive
    global numnontrivialchecks
    global numpositivenontrivial

    if _selectors_overlap_memo.has_key((css1, css2)):
        return _selectors_overlap_memo[(css1, css2)]
    elif _selectors_overlap_memo.has_key((css2, css1)):
        return _selectors_overlap_memo[(css2, css1)]
    else:
        numchecks += 1
        fast_res = _shortcut_selectors_overlap(css1, css2)
        if fast_res is not None:
            if fast_res:
                numpositive += 1
            return fast_res
        numnontrivialchecks += 1
        aut1 = _make_selector_automata(css1)
        aut2 = _make_selector_automata(css2)
        aut = cssautomaton.intersect(aut1, aut2)
        result = not autemptiness.isempty(aut, (cssfile.selector_str(css1), cssfile.selector_str(css2)))
        _selectors_overlap_memo[(css1, css2)] = result
        if result:
            numpositive += 1
            numpositivenontrivial += 1
        return result

def _shortcut_selectors_overlap(css1, css2):
    """Implements some fast checks for selector overlap
    :param css1:
        css selector as cssselect parsed_tree
    :param css2:
        css selector as cssselect parsed_tree
    :returns:
        True/False if a quick diagnosis of overlap between selectors could be made
        else None
    """

    def is_star(css):
        """
        :param css:
            css selector as parsed tree
        :returns:
            True iff css is .c for some c
        """
        return (type(css).__name__ == "Element" and
                css.namespace == None and
                css.element == None)

    def is_class(css):
        """
        :param css:
            css selector as parsed tree
        :returns:
            True iff css is .c for some c
        """
        return (type(css).__name__ == "Class" and
                is_star(css.selector))

    def is_hash(css):
        """
        :param css:
            css selector as parsed tree
        :returns:
            True iff css is #i for some i
        """
        return (type(css).__name__== "Hash" and
                is_star(css.selector))

    def is_element(css):
        """
        :param css:
            css selector as parsed tree
        :returns:
            True iff css is n|e for some n|e
        """
        return type(css).__name__== "Element"

    def all_classes_pseudo(css):
        """
        :param css:
            css selector as parsed tree
        :returns:
            True iff css is a complex selector built only from .c atoms
            e.g. .c > .d
            p as string if css is complex selector built only from .c atoms but
            ending with :p
        """
        if is_star(css):
            return True
        elif (type(css).__name__ == "Class" and
              all_classes_pseudo(css.selector) is not False):
            return True
        elif (type(css).__name__ == "CombinedSelector" and
              all_classes_pseudo(css.selector) is not False and
              all_classes_pseudo(css.subselector) is not False):
            return True
        elif (type(css).__name__ == "Pseudo" and
              all_classes_pseudo(css.selector) is not False):
            return css.ident
        else:
            return False

    if is_class(css1) and is_class(css2):
        return True
    elif is_hash(css1) and is_hash(css2):
        return css1.id == css2.id
    elif is_element(css1) and is_element(css2):
        return css1 == css2

    p1 = all_classes_pseudo(css1)
    p2 = all_classes_pseudo(css2)
    if not(p1 is False or p2 is False):
        if p1 is True or p2 is True:
            return True
        elif ((p1, p2) in autemptiness.get_local_conflict_ps() or
              (p2, p1) in autemptiness.get_local_conflict_ps()):
            return False

    return None

def _make_selector_automata(css):
    """
    Note: is memoized, call reset_selectors_overlap_memo before using

    :param css:
        A css selector in parsed_tree cssselect format
    :returns:
        An automaton representation of the selector
    """
    if _selectors_automata.has_key(css):
        return _selectors_automata[css]
    else:
        aut = cssautomaton.fromselector(css)
        _selectors_automata[css] = aut
        return aut

