
import abc
import unittest
import re

import cssselect_parser
from lxml import etree

import cssautomaton
from cssautomaton import *

import autemptiness
from autemptiness import *

import simplecssbuilder

from simpleCSS import *


from z3 import *

def _parse_selector(selector):
    return cssselect_parser.parse(selector).pop().parsed_tree

_isany = _parse_selector("*")


class TestAutomatonConstruction(unittest.TestCase):

    # These can possibly be rewritten to use aut.parse_tran_list

    def test_class(self):
        css = _parse_selector(".c")
        aut_built = cssautomaton.fromselector(css)
        #   _>,~_
        #  /     \
        #  \     /  .
        #    qin ------> qfin
        #          .c
        aut = CSSAutomaton()
        aut.qinit = aut._new_state()
        aut.qfinal = aut._new_state()
        aut.add_tran(Tran(aut.qinit, Arrow.child, _isany, aut.qinit))
        aut.add_tran(Tran(aut.qinit, Arrow.sibling, _isany, aut.qinit))
        aut.add_tran(Tran(aut.qinit, Arrow.noop, css, aut.qfinal))
        self.assertEqual(aut, aut_built)

    def test_child(self):
        css = _parse_selector(".c > img")
        cls = _parse_selector(".c")
        img = _parse_selector("img")
        aut_built = cssautomaton.fromselector(css)
        #   _>,~_   ______>__________
        #  /     \ /     .c          \
        #  \     // >            ~    \       .
        #    qin ------> qloop ------> qmid ------> qfin
        #          .c            *            img
        aut = CSSAutomaton()
        aut.qinit = aut._new_state()
        aut.qfinal = aut._new_state()
        aut.add_tran(Tran(aut.qinit, Arrow.child, _isany, aut.qinit))
        aut.add_tran(Tran(aut.qinit, Arrow.sibling, _isany, aut.qinit))
        qmid = aut._new_state()
        qloop = aut._new_state()
        aut.add_tran(Tran(aut.qinit, Arrow.child, cls, qmid))
        aut.add_tran(Tran(aut.qinit, Arrow.child, cls, qloop))
        aut.add_tran(Tran(qloop, Arrow.sibling, _isany, qmid))
        aut.add_tran(Tran(qmid, Arrow.noop, img, aut.qfinal))
        self.assertEqual(aut, aut_built)

    def test_descendant(self):
        css = _parse_selector(".c img")
        cls = _parse_selector(".c")
        img = _parse_selector("img")
        aut_built = cssautomaton.fromselector(css)
        aut = CSSAutomaton()
        #   _>,~_   ______>__________
        #  /     \ /     .c          \
        #  \     // >            >,~  \       .
        #    qin ------> qloop ------> qmid ------> qfin
        #          .c   /     \  *            img
        #               \_>,~_/
        #                  *
        aut.qinit = aut._new_state()
        aut.qfinal = aut._new_state()
        aut.add_tran(Tran(aut.qinit, Arrow.child, _isany, aut.qinit))
        aut.add_tran(Tran(aut.qinit, Arrow.sibling, _isany, aut.qinit))
        qmid = aut._new_state()
        qloop = aut._new_state()
        aut.add_tran(Tran(aut.qinit, Arrow.child, cls, qmid))
        aut.add_tran(Tran(aut.qinit, Arrow.child, cls, qloop))
        aut.add_tran(Tran(qloop, Arrow.child, _isany, qloop))
        aut.add_tran(Tran(qloop, Arrow.sibling, _isany, qloop))
        aut.add_tran(Tran(qloop, Arrow.child, _isany, qmid))
        aut.add_tran(Tran(qloop, Arrow.neighbour, _isany, qmid))
        aut.add_tran(Tran(qmid, Arrow.noop, img, aut.qfinal))
        self.assertEqual(aut, aut_built)

    def test_neighbour(self):
        css = _parse_selector(".c + img")
        cls = _parse_selector(".c")
        img = _parse_selector("img")
        aut_built = cssautomaton.fromselector(css)
        #   _>,~_
        #  /     \
        #  \     /  +            .
        #    qin ------> qmid ------> qfin
        #          .c           img
        aut = CSSAutomaton()
        aut.qinit = aut._new_state()
        aut.qfinal = aut._new_state()
        qmid = aut._new_state()
        aut.add_tran(Tran(aut.qinit, Arrow.child, _isany, aut.qinit))
        aut.add_tran(Tran(aut.qinit, Arrow.sibling, _isany, aut.qinit))
        aut.add_tran(Tran(aut.qinit, Arrow.neighbour, cls, qmid))
        aut.add_tran(Tran(qmid, Arrow.noop, img, aut.qfinal))
        self.assertEqual(aut, aut_built)

    def test_sibling(self):
        css = _parse_selector(".c ~ img")
        cls = _parse_selector(".c")
        img = _parse_selector("img")
        aut_built = cssautomaton.fromselector(css)
        #   _>,~_   ______+__________
        #  /     \ /     .c          \
        #  \     // +            +    \       .
        #    qin ------> qloop ------> qmid ------> qfin
        #          .c   /     \  *            img
        #               \__~__/
        #                  *
        aut = CSSAutomaton()
        aut.qinit = aut._new_state()
        aut.qfinal = aut._new_state()
        aut.add_tran(Tran(aut.qinit, Arrow.child, _isany, aut.qinit))
        aut.add_tran(Tran(aut.qinit, Arrow.sibling, _isany, aut.qinit))
        qmid = aut._new_state()
        qloop = aut._new_state()
        aut.add_tran(Tran(aut.qinit, Arrow.neighbour, cls, qmid))
        aut.add_tran(Tran(aut.qinit, Arrow.neighbour, cls, qloop))
        aut.add_tran(Tran(qloop, Arrow.sibling, _isany, qloop))
        aut.add_tran(Tran(qloop, Arrow.neighbour, _isany, qmid))
        aut.add_tran(Tran(qmid, Arrow.noop, img, aut.qfinal))
        self.assertEqual(aut, aut_built)

    def test_complex_node_selector(self):
        css = _parse_selector(".c[s|a |= yes]#id:disabled:not(:nth-child(3n+4))")
        aut_built = cssautomaton.fromselector(css)
        #   _>,~_
        #  /     \
        #  \     /  .
        #    qin ------> qfin
        #          css
        aut = CSSAutomaton()
        aut.qinit = aut._new_state()
        aut.qfinal = aut._new_state()
        aut.add_tran(Tran(aut.qinit, Arrow.child, _isany, aut.qinit))
        aut.add_tran(Tran(aut.qinit, Arrow.sibling, _isany, aut.qinit))
        aut.add_tran(Tran(aut.qinit, Arrow.noop, css, aut.qfinal))
        self.assertEqual(aut, aut_built)

    def test_chained_selectors(self):
        css = _parse_selector(".c img ~ :active")
        cls = _parse_selector(".c")
        img = _parse_selector("img")
        act = _parse_selector(":active")
        aut_built = cssautomaton.fromselector(css)
        #   _>,~_   ______>__________       ______+__________
        #  /     \ /     .c          \     /     img         \
        #  \     // >            >,~  \   / +             +   \       .
        #    qin ------> qloop1 -----> q1 ------> qloop2 -----> qtwo ------> qfin
        #          .c   /     \  *          img  /     \  *          :active
        #               \_>,~_/                  \__~__/
        #                  *                        *
        aut = CSSAutomaton()
        aut.qinit = aut._new_state()
        aut.qfinal = aut._new_state()
        aut.add_tran(Tran(aut.qinit, Arrow.child, _isany, aut.qinit))
        aut.add_tran(Tran(aut.qinit, Arrow.sibling, _isany, aut.qinit))

        # kind of rubbish we have to get these in the same order as the aut
        # construction, but i don't know how to solve graph isomorphism easily
        q2 = aut._new_state()
        q1 = aut._new_state()
        qloop1 = aut._new_state()
        qloop2 = aut._new_state()

        aut.add_tran(Tran(aut.qinit, Arrow.child, cls, q1))
        aut.add_tran(Tran(aut.qinit, Arrow.child, cls, qloop1))
        aut.add_tran(Tran(qloop1, Arrow.child, _isany, qloop1))
        aut.add_tran(Tran(qloop1, Arrow.sibling, _isany, qloop1))
        aut.add_tran(Tran(qloop1, Arrow.child, _isany, q1))
        aut.add_tran(Tran(qloop1, Arrow.neighbour, _isany, q1))

        aut.add_tran(Tran(q1, Arrow.neighbour, img, q2))
        aut.add_tran(Tran(q1, Arrow.neighbour, img, qloop2))
        aut.add_tran(Tran(qloop2, Arrow.sibling, _isany, qloop2))
        aut.add_tran(Tran(qloop2, Arrow.neighbour, _isany, q2))

        aut.add_tran(Tran(q2, Arrow.noop, act, aut.qfinal))

        self.assertEqual(aut, aut_built)


class TestAccepts(unittest.TestCase):

    def test_simple_accept_child(self):
        ele1 = _parse_selector("ele1")
        ele2 = _parse_selector("ele2")
        aut = CSSAutomaton()
        #           >                 .
        # qinit ---------> qmid ------------> qfinal
        #          ele1              ele2
        aut.qinit = aut._new_state()
        aut.qfinal = aut._new_state()
        qmid = aut._new_state()
        aut.add_tran(Tran(aut.qinit, Arrow.child, ele1, qmid))
        aut.add_tran(Tran(qmid, Arrow.noop, ele2, aut.qfinal))

        tree = etree.fromstring("<ele1><ele2/></ele1>")
        child = list(tree).pop()
        self.assertTrue(aut.accepts(child))

    def test_simple_reject_child(self):
        ele1 = _parse_selector("ele1")
        ele2 = _parse_selector("ele2")
        aut = CSSAutomaton()
        #           >                 .
        # qinit ---------> qmid ------------> qfinal
        #          ele1              ele2
        aut.qinit = aut._new_state()
        aut.qfinal = aut._new_state()
        qmid = aut._new_state()
        aut.add_tran(Tran(aut.qinit, Arrow.child, ele1, qmid))
        aut.add_tran(Tran(qmid, Arrow.noop, ele2, aut.qfinal))

        tree = etree.fromstring("<ele1><ele1/></ele1>")
        child = list(tree).pop()
        self.assertFalse(aut.accepts(child))

    def test_simple_accept_neighbour(self):
        ele1 = _parse_selector("ele1")
        ele2 = _parse_selector("ele2")
        aut = CSSAutomaton()
        #  >,~
        # |   |     +                 .
        # qinit ---------> qmid ------------> qfinal
        #          ele1              ele2
        aut.qinit = aut._new_state()
        aut.qfinal = aut._new_state()
        qmid = aut._new_state()
        aut.add_tran(Tran(aut.qinit, Arrow.sibling, _isany, aut.qinit))
        aut.add_tran(Tran(aut.qinit, Arrow.child, _isany, aut.qinit))
        aut.add_tran(Tran(aut.qinit, Arrow.neighbour, ele1, qmid))
        aut.add_tran(Tran(qmid, Arrow.noop, ele2, aut.qfinal))

        tree = etree.fromstring("<ele><ele1/><ele2/></ele>")
        neighbour = list(tree).pop(1)
        self.assertTrue(aut.accepts(neighbour))

    def test_simple_reject_neighbour(self):
        ele1 = _parse_selector("ele1")
        ele2 = _parse_selector("ele2")
        aut = CSSAutomaton()
        #           +                .
        # qinit ---------> qmid ------------> qfinal
        #          ele1              ele2
        aut.qinit = aut._new_state()
        aut.qfinal = aut._new_state()
        qmid = aut._new_state()
        aut.add_tran(Tran(aut.qinit, Arrow.neighbour, ele1, qmid))
        aut.add_tran(Tran(qmid, Arrow.noop, ele2, aut.qfinal))

        tree = etree.fromstring("<ele><ele1/><ele1/></ele>")
        neighbour = list(tree).pop()
        self.assertFalse(aut.accepts(neighbour))


    def test_simple_accept_sibling(self):
        ele1 = _parse_selector("ele1")
        ele2 = _parse_selector("ele2")
        aut = CSSAutomaton()
        #  >,~              ~
        # |   |     +      | |        .
        # qinit ---------> qmid ------------> qfinal
        #          ele1              ele2
        aut.qinit = aut._new_state()
        aut.qfinal = aut._new_state()
        qmid = aut._new_state()
        aut.add_tran(Tran(aut.qinit, Arrow.sibling, _isany, aut.qinit))
        aut.add_tran(Tran(aut.qinit, Arrow.child, _isany, aut.qinit))
        aut.add_tran(Tran(aut.qinit, Arrow.neighbour, ele1, qmid))
        aut.add_tran(Tran(qmid, Arrow.sibling, _isany, qmid))
        aut.add_tran(Tran(qmid, Arrow.noop, ele2, aut.qfinal))

        tree = etree.fromstring("<ele><ele1/><ele1/><ele1/><ele2/></ele>")
        sibling = list(tree).pop(3)
        self.assertTrue(aut.accepts(sibling))

    def test_simple_reject_sibling(self):
        ele1 = _parse_selector("ele1")
        ele2 = _parse_selector("ele2")
        aut = CSSAutomaton()
        #  >,~              ~
        # |   |     +      | |        .
        # qinit ---------> qmid ------------> qfinal
        #          ele1              ele2
        aut.qinit = aut._new_state()
        aut.qfinal = aut._new_state()
        qmid = aut._new_state()
        aut.add_tran(Tran(aut.qinit, Arrow.sibling, _isany, aut.qinit))
        aut.add_tran(Tran(aut.qinit, Arrow.child, _isany, aut.qinit))
        aut.add_tran(Tran(aut.qinit, Arrow.neighbour, ele1, qmid))
        aut.add_tran(Tran(qmid, Arrow.sibling, _isany, qmid))
        aut.add_tran(Tran(qmid, Arrow.noop, ele2, aut.qfinal))

        tree = etree.fromstring("<ele><ele2/><ele2/><ele2/><ele2/></ele>")
        sibling = list(tree).pop(3)
        self.assertFalse(aut.accepts(sibling))


class TestIntersection(unittest.TestCase):

    def __do_test(self, css1, css2, tree, result, namespaces = {}):
        """Gets the intersection of css1 and css2, and tests if the node with id
           "m" is matched and asserts result is as expected.

        :param css1:
            The first CSS selector as string
        :param css2:
            The second CSS selector as string
        :param tree:
            An XML tree as string, with a node with id 'm'
        :param result:
            Whether the intersection of the selectors should match 'm'
        :param namespaces:
            Any needed namespaces as dict of 'namespace' : 'uri' pairs
        """
        aut1 = cssautomaton.fromstring(css1, namespaces)
        aut2 = cssautomaton.fromstring(css2, namespaces)
        aut = cssautomaton.intersect(aut1, aut2)
        tree = etree.fromstring(tree)
        m = CSSSelector("#m")(tree).pop()
        self.assertEqual(aut.accepts(m), result)



    def test_basic_accept(self):
        self.__do_test("img", "ns|*",
                       "<eles xmlns:ns='ns'><ns:img id='m'/></eles>",
                       True,
                       { 'ns' : 'ns' })

    def test_basic_reject(self):
        self.__do_test("img", "a",
                       "<eles xmlns:ns='ns'><ns:img id='m'/></eles>",
                       False,
                       { 'ns' : 'ns' })

    def test_combined_node_selectors_accept(self):
        self.__do_test("img[a='v']:only-child", "[b='u']",
                       "<eles><img id='m' a='v' b='u'/></eles>",
                       True)

    def test_combined_node_selectors_reject(self):
        self.__do_test("img[a='v']:only-child", "[a='u']",
                       "<eles><img id='m' a='v' b='u'/></eles>",
                       False)

    def test_diverging_selectors_accept(self):
        self.__do_test("e1 > e2 ~ e3 e4", "e1 > e5 ~ * > e6 e4",
                       """<e1>
                            <e2/>
                            <e/>
                            <e5/>
                            <e/>
                            <e3>
                              <e6>
                                <e>
                                  <e4 id='m'/>
                                </e>
                              </e6>
                            </e3>
                            <e/>
                          </e1>""",
                       True)

    def test_diverging_selectors_reject(self):
        self.__do_test("e1 > e2 ~ e3 e4", "e1 > e5 ~ * > e4",
                       """<e1>
                            <e2/>
                            <e/>
                            <e5/>
                            <e/>
                            <e3>
                              <e6>
                                <e>
                                  <e4 id='m'/>
                                </e>
                              </e6>
                            </e3>
                            <e/>
                          </e1>""",
                       False)

class TestEmptinessSelNormalisation(unittest.TestCase):

    def _do_test(self, sel, nsel):
        """Tests whether sel, after class normalisation, is nsel

        :param sel:
            The css selector as a string
        :param sel:
            The normalised sel as a string or None if unsat because of classes
        """
        css = _parse_selector(sel)
        ncss = autemptiness._normalise_selector(css)

        exp = _parse_selector(nsel) if nsel is not None else None

        self.assertEqual(str(ncss), str(exp))

    def test_simple_cls(self):
        self._do_test("*.c", "*")

    def test_simple_cls_neg(self):
        self._do_test("*.c:not(.d)", "*")

#   fails because stringcons not implemented
#    def test_simple_cls_inconsistent(self):
#        self._do_test("*.c:not(.c)", None)

    # TODO: can't sensibly test IDs until stringcons is implemented

    def test_class_attr(self):
        self._do_test("[class~='c'].d:target", ":target")

    def test_class_attr(self):
        self._do_test("[class~='c'].d:target", ":target")

    def test_simple_attr(self):
        self._do_test("[ns|a*='b'][*|a*='c']:not([*|a='d']):target", ":target")

    # TODO: can't really test consistency checks since it's not implemented

    def test_pseudo_simple(self):
        self._do_test("e:hover", "e")

    def test_pseudo_conflict_link(self):
        self._do_test("e:link:visited", None)

    def test_pseudo_conflict_enabled(self):
        self._do_test("e:enabled:disabled", None)

    def test_pseudo_mix(self):
        self._do_test("e:visited:hover:active:target:focus:enabled:checked:nth-child(3)", "e:target:nth-child(3)")

    def test_pseudo_not(self):
        self._do_test("e:not(:visited):hover", "e")

    def test_pseudo_not_conflict(self):
        self._do_test("e:not(:visited):visited", None)


class TestEmptinessAutNormalisation(unittest.TestCase):

    def _do_test(self, aut, naut):
        """Tests whether aut normalises to naut.

        :param aut:
            String list representation of aut
        :param naut:
            String list representation of normalised aut
        """
        a = cssautomaton.fromlist(aut)
        na = cssautomaton.fromlist(naut)
        self.assertEqual(autemptiness._normalise_automaton(a), na)

    def test_simple_norm(self):
        self._do_test(["q0", "q1",
                       "q0 -- c, e:active[a = 'v'].c --> q2",
                       "q2 -- n, e:active:not(:active) --> q3",
                       "q3 -- s, :nth-child(3) --> q4",
                       "q4 -- 0, * --> q1"],
                      ["q0", "q1",
                       "q0 -- c, e --> q2",
                       "q3 -- s, :nth-child(3) --> q4",
                       "q4 -- 0, * --> q1"])

class TestNodeSelectorEmptiness(unittest.TestCase):

    def _do_test(self, css, result):
        """
        :param css"
            String, CSS selector
        :param result:
            True iff the selector should be empty
        """
        aut = cssautomaton.fromstring(css)
        self.assertEqual(autemptiness.isempty(aut), result)

    # TODO: add tests including attributes and ids

    def test_simple(self):
        self._do_test(".c", False)

    def test_empty_unsat(self):
        self._do_test(":empty:not(:empty)", True)

    def test_element_nonemp(self):
        self._do_test("e:empty", False)

    def test_element_emp(self):
        self._do_test("e:empty:not(e)", True)

    def test_namespace_nonemp(self):
        self._do_test("ns|*:empty", False)

    def test_namespace_emp(self):
        self._do_test("ns|*:empty:not(ns|*)", True)

    def test_ele_namespace_emp(self):
        self._do_test("ns|e:empty:not(*|e)", True)

    def test_namespace_ele_nonemp(self):
        self._do_test("*|e:not(ns|e)", False)

    def test_nth_child_parse1(self):
        self._do_test("e:nth-child(3n+4):not(:empty)", False)

    def test_nth_child_parse2(self):
        self._do_test("e:nth-child(n+4):not(:empty)", False)

    def test_nth_child_parse3(self):
        self._do_test("e:nth-child(3n+4):not(:empty)", False)

    def test_nth_child_parse4(self):
        self._do_test("e:nth-child(n+4):not(:empty)", False)

    def test_nth_child_emp(self):
        self._do_test("e:nth-child(3n):nth-child(6n+1)", True)

    def test_nth_child_neg_nonemp(self):
        self._do_test(":not(:nth-child(2n+1))", False)

    def test_nth_child_neg_emp(self):
        self._do_test(":nth-child(4n):not(:nth-child(2n))", True)

    def test_nth_last_child_emp(self):
        self._do_test("e:nth-last-child(3n):nth-last-child(6n+1)", True)

    def test_nth_last_child_neg_nonemp(self):
        self._do_test(":not(:nth-last-child(2n+1))", False)

    def test_nth_last_child_neg_emp(self):
        self._do_test(":nth-last-child(4n):not(:nth-last-child(2n))", True)

    def test_nth_of_type_emp(self):
        self._do_test("e:nth-of-type(3n):nth-of-type(6n+1)", True)

    def test_nth_of_type_neg_nonemp(self):
        self._do_test(":not(:nth-of-type(2n+1))", False)

    def test_nth_of_type_neg_emp(self):
        self._do_test(":nth-of-type(4n):not(:nth-of-type(2n))", True)

    def test_nth_last_of_type_emp(self):
        self._do_test("e:nth-last-of-type(3n):nth-last-of-type(6n+1)", True)

    def test_nth_last_of_type_neg_nonemp(self):
        self._do_test(":not(:nth-last-of-type(2n+1))", False)

    def test_nth_last_of_type_neg_emp(self):
        self._do_test(":nth-last-of-type(4n):not(:nth-last-of-type(2n))", True)

    def test_first_child_emp(self):
        self._do_test("e:nth-child(3n):first-child", True)

    def test_first_child_neg_nonemp(self):
        self._do_test(":not(:first-child)", False)

    def test_first_child_neg_emp(self):
        self._do_test(":nth-child(1):not(:first-child)", True)




class TestEmptiness(unittest.TestCase):

    def _do_test(self, css, result):
        """
        :param css"
            String, CSS selector
        :param result:
            True iff the selector should be empty
        """
        aut = cssautomaton.fromstring(css)
        self.assertEqual(autemptiness.isempty(aut), result)

    #TODO: write some tests and uncomment one below once implemented

    def test_simple_nonemp(self):
        self._do_test(".c", False)

    def test_simple_emp(self):
        self._do_test("e:not(e)", True)

    def test_simple_run_nonemp(self):
        self._do_test(".c > e1 + e2", False)

    def test_simple_run_emp(self):
        self._do_test(".c > e1 + e2:first-child", True)

    def test_nth_child_run_nonemp(self):
        self._do_test("e1 > e2:nth-child(3n) + e1:nth-child(3n+1) e2", False)

    def test_nth_child_run_emp(self):
        self._do_test("e1 > e2:nth-child(3n) + e1:nth-child(3n+2) e2", True)

    def test_nth_last_child_run_nonemp(self):
        self._do_test("e1 > e2:nth-last-child(3n) + e1:nth-last-child(3n+2) e2", False)

    def test_nth_last_child_run_emp(self):
        self._do_test("e1 > e2:nth-last-child(3n) + e1:nth-last-child(3n+1) e2", True)

    def test_nth_of_type_run_nonemp(self):
        self._do_test("e1 > a|e2:nth-of-type(3n) + a|e1:nth-of-type(3n+1) e2", False)

    def test_nth_of_type_run_nonemp_ns(self):
        self._do_test("e1 > e2:nth-of-type(3n) + e1:nth-of-type(3n+2) e2", False)

    def test_nth_of_type_run_emp(self):
        self._do_test("e1 > a|e1:nth-of-type(3n) + a|e1:nth-of-type(3n+2) e2", True)

    def test_nth_last_of_type_run_nonemp(self):
        self._do_test("e1 > a|e2:nth-last-of-type(3n) + a|e1:nth-last-of-type(3n+2) e2", False)

    def test_nth_last_of_type_run_nonemp_ns(self):
        self._do_test("e1 > e2:nth-last-of-type(3n) + e1:nth-last-of-type(3n+1) e2", False)

    def test_nth_last_of_type_run_emp(self):
        self._do_test("e1 > a|e1:nth-last-of-type(3n) + a|e1:nth-last-of-type(3n+1) e2", True)

    def test_mixture_nonemp(self):
        self._do_test("e1 > :nth-child(4n + 4) + :only-of-type", False)

    def test_mixture_emp(self):
        self._do_test("e1 > :nth-child(4n + 4) + a|e:only-of-type + a|e:nth-last-of-type(1)", True)

    def test_mixture_emp_simple(self):
        self._do_test("a|e:only-of-type + a|e:only-of-type", True)

    def test_empty_child_emp(self):
        self._do_test("e1 > e2:empty > e1", True)

    def test_empty_child_nonemp(self):
        self._do_test("e1 > e2:empty ~ e2 > e1", False)

    def test_target_emp(self):
        self._do_test("e1:target ~ e1 > e2:target", True)

    def test_target_nonemp(self):
        self._do_test("e1:target ~ e1 > e2", False)

    def test_root_emp(self):
        self._do_test("e1:root ~ e1 > e2", True)

    def test_target_nonemp(self):
        self._do_test("e1:root > e1 > e2", False)

    def test_root_sib(self):
        self._do_test(":root ~ :nth-child(n)", True)

    def test_root_first_child(self):
        self._do_test(":root:first-child > :nth-child(2)", True)

    def test_not_first_child(self):
        self._do_test(".c > e1 + e2:not(:first-child)", False)

    def test_not_first_child_emp(self):
       self._do_test(".c > e1:nth-child(0):not(:first-child) + e2:not(:first-child)", True)

    def test_not_nth_child_run_emp(self):
        self._do_test("e1 > e2:nth-child(3n) + e1:not(:nth-child(3n+1)) e2", True)

    def test_not_nth_child_run_nonemp(self):
        self._do_test("e1 > e2:nth-child(3n) + e1:not(:nth-child(3n+2)) e2", False)

    def test_not_last_child(self):
        self._do_test(".c > e2:not(:last-child)", False)

    def test_not_last_child_emp(self):
       self._do_test(".c > e2:not(:last-child) + e1:nth-last-child(0):not(:last-child)", True)

    def test_not_nth_last_child_run_emp(self):
        self._do_test("e1 > e2:nth-last-child(3n+1) + e1:not(:nth-last-child(3n)) e2", True)

    def test_not_nth_last_child_run_nonemp(self):
        self._do_test("e1 > e2:nth-last-child(3n+2) + e1:not(:nth-last-child(3n)) e2", False)

    def test_nth_nth_last_emp(self):
        self._do_test("e1 > e2:first-child:nth-last-child(3n+1) ~ e1:last-child:nth-child(3n)", True)

    def test_nth_nth_last_nonemp(self):
        self._do_test("e1 > e2:first-child:nth-last-child(3n) ~ e1:last-child:nth-child(3n)", False)

    def test_nth_nth_last_nonemp_simp(self):
        self._do_test("e2:nth-last-child(3n) ~ e1:last-child", False)

    def test_not_nth_child_run_emp(self):
        self._do_test("e1 > e2:nth-child(3n) + e1:not(:nth-child(3n+1)) e2", True)

    def test_not_nth_child_run_nonemp(self):
        self._do_test("e1 > e2:nth-child(3n) + e1:not(:nth-child(3n+2)) e2", False)

    def test_nth_nth_last_emp_sat(self):
        self._do_test("e1 > e2:first-child:nth-last-child(3n+1) ~ e1:last-child:nth-child(3n) e2:only-of-type", True)

    def test_nth_nth_last_nonemp_sat(self):
        self._do_test("e1 > e2:first-child:nth-last-child(3n) ~ e1:last-child:nth-child(3n) e2:only-of-type", False)

    def test_nth_nth_last_nonemp_sat_simp(self):
        self._do_test(":first-child", False)

    def test_not_nth_child_run_emp_sat(self):
        self._do_test("e1 > e2:nth-child(3n) + e1:not(:nth-child(3n+1)) e2:only-of-type", True)

    def test_not_nth_child_run_nonemp_sat(self):
        self._do_test("e1 > e2:nth-child(3n) + e1:not(:nth-child(3n+2)) e2:only-of-type", False)

    def test_not_nth_last_child_run_emp_sat(self):
        self._do_test("e1 > e2:nth-last-child(3n+1) + e1:not(:nth-last-child(3n)) e2:only-of-type", True)

    def test_not_nth_last_child_run_nonemp_sat(self):
        self._do_test("e1 > e2:nth-last-child(3n+2) + e1:not(:nth-last-child(3n)) e2:only-of-type", False)

    def test_simple_bad_not_nth_sat(self):
        self._do_test(":nth-child(2) + :not(:nth-child(3)) e2:only-of-type", True)


class TestIntersectionEmptiness(unittest.TestCase):

    def _do_test(self, css1, css2, result):
        """
        :param css1"
            String, CSS selector
        :param css2:
            String, CSS selector
        :param result:
            True iff the intersection of the selectors should be empty
        """
        aut1 = cssautomaton.fromstring(css1)
        aut2 = cssautomaton.fromstring(css2)
        aut = cssautomaton.intersect(aut1, aut2)
        self.assertEqual(autemptiness.isempty(aut), result)

    def test_simple_emp(self):
        self._do_test("e1", "e2", True)

    def test_simple_nonemp(self):
        self._do_test("e1", "e1", False)

    def test_diverge_nonemp(self):
        self._do_test("e1 > e1 ~ e2", "e1 > e2", False)

    def test_diverge_nonemp2(self):
        self._do_test("e1 > e1 ~ e2", "e1 > e2 ~ e2", False)

    def test_diverge_emp(self):
        self._do_test("e1 > e1 > e2", "e1 > e2 > e2", True)

    def test_nth_child_nonemp(self):
        self._do_test(":nth-child(3n) + e", "e:nth-child(6n+1)", False)

    def test_nth_child_emp(self):
        self._do_test(":nth-child(3n) + e", "e:nth-child(6n+2)", True)

    def test_of_type_nonemp(self):
        self._do_test(":nth-of-type(1)", "e > :first-child + a|e", False)

    def test_of_type_emp(self):
        self._do_test(":nth-of-type(1)", "e > a|e:first-child + a|e", True)

class TestSimpleCSSBuilder(unittest.TestCase):

    def _do_test(self, css, simplecss):
        """Tests whether simplecssbuilder produces the expected simplecss.

        :param css:
            The css to transform, as a string
        :param simplecss:
            The simplecss expected, as a string
        """
        sim = simplecssbuilder.fromstring(css)
        want = _read_simple_css(simplecss)
        # ignore the complexRules part...
        self.assertEqual(set(sim.edgeList), set(want.edgeList))
        self.assertEqual(set(sim.edgeOrder), set(want.edgeOrder))

    def test_simple(self):
        self._do_test("""img { margin: 0; width: 100% }""",
                      """1: img { margin: 0 }
                         2: img { width: 100% }""")

    def test_simple_order(self):
        self._do_test("""*.c { margin: 0; width: 100% }
                         *.c { margin: 4 }""",
                      """1: *.c { margin: 0 }
                         2: *.c { width: 100% }
                         3: *.c { margin: 4 }
                         1 < 3""")

    def test_specificity(self):
        self._do_test("""*.c { margin: 0; width: 100% }
                         e { margin: 4 }""",
                      """1: *.c { margin: 0 }
                         2: *.c { width: 100% }
                         3: e { margin: 4 }""")

    def test_complex_selectors(self):
        self._do_test("""*.c > img ~ a { margin: 4; width: 75% }
                         *.c > img ~ a { font-size: 12pt }
                         *:target ~ div ~ a { margin: 7 }""",
                      """1: *.c > img ~ a { margin: 4 }
                         2: *.c > img ~ a { width: 75% }
                         3: *.c > img ~ a { font-size: 12pt }
                         4: *:target ~ div ~ a { margin: 7 }
                         1 < 4""")

    def test_loop(self):
        self._do_test("""*.a { margin: 0 }
                         *.b { margin: 1 }
                         *.a { margin: 0 }""",
                      """1: *.a { margin: 0 }
                         2: *.b { margin: 1 }
                         3: *.a { margin: 0 }
                         2 < 3""")


################################################################
## Helper functions

_simpleRE = re.compile("\s*((\d*):)?\s*(.*?)\s*{\s*(\S*)\s*:\s*(.*?)\s*}\s*")
_id_grp = 2
_sel_grp = 3
_prop_grp = 4
_val_grp = 5

_orderRE = re.compile("\s*(\d*)\s*<\s*(\d*)\s*")
_conflictRE = re.compile("\s*(\d*)\s*#\s*(\d*)\s*")
_lhs_grp = 1
_rhs_grp = 2


def _read_simple_css(simplecss):
    """Parses simple css in the format

        id: selector { property: value }

    where id is a number.  Ordering given by lines

        id < id

    :param simplecss:
        Some simple css as a string
    :returns:
        a simpleCSS object built from the string
    """
    return _read_simple_css_full(simplecss)[0]

def _read_simple_css_full(simplecss):
    """Parses simple css in the format

        id: selector { property: value }

    where id is a number.  Ordering given by lines

        id < id

    and conflicts by

        id # id

    :param simplecss:
        Some simple css as a string
    :returns:
        (css, rules, conflicts)
        css - a simpleCSS object built from the string
        rules - a map from ids to simpleRules
        conflicts - a set of pairs (e1, e2) of simpleRules which are conflicting
    """
    rules = {}
    order = []
    conflicts = set()
    for line in simplecss.split('\n'):
        res = _read_simple_rule(line)
        if res is not None:
            i = res[0]
            rules[i] = res[1]
        else:
            m = _orderRE.match(line)
            if m is not None:
                order.append((rules[m.group(_lhs_grp)],
                              rules[m.group(_rhs_grp)]))
            else:
                m = _conflictRE.match(line)
                if m is not None:
                    conflicts.add((rules[m.group(_lhs_grp)],
                                   rules[m.group(_rhs_grp)]))
    return (simpleCSS(list(rules.values()), order), rules, conflicts)

def _read_simple_rule(rule):
    """"
    :param rule:
        String in format (i: )? selector { prop }
    :returns:
        None if not in format or tuple
        (i, r)
            where i is None or value of i if present
                  r is the rule as simpleRule
    """
    m = _simpleRE.match(rule)
    if m is not None:
        i = m.group(_id_grp)
        r = simplecssbuilder._make_simple_rule(m.group(_prop_grp),
                                               m.group(_sel_grp),
                                               m.group(_val_grp))
        return (i, r)
    return None



###################################################################
## Main

if __name__ == '__main__':
    unittest.main()
