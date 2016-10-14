"""A representation of CSS files as cliques of selectors and properties"""

from itertools import product

from cssfile import selector_str
from simpleCSS import *

__DEBUG__ = True

class cliqueCSS:

    def __init__(self, cliques = None, prop_names = dict()):
        """
        :param cliques:
            A list of pairs (ss, ps) where ss is a set of selectors in the same format as simpleRule
            selectors and ps is a set of properties in the same format as simpleRule
        :param prop_names:
            a map from properties (of the form "p: v" to the name of the
            property defined (p)
        """
        if cliques == None:
            self.cliques = []
        else:
            self.cliques = list(cliques)

        self.prop_names = prop_names

    def add_rule(self, selectors, properties):
        """Adds the rule selectors { properties } to the CSS

        :param selectors:
            A set of selectors in same format as simpleRule
        :param properties:
            A list of properties represented same as in simpleRule, where the
            ordering reflects the order they should appear in the file
        """
        self.cliques.append((selectors, properties))

    def num_rules(self):
        return len(self.cliques)

    def last_index_of(self, r, i = 0):
        """
        :param r:
            A simpleRule
        :param i:
            An index in range(self.num_rules())
        :returns:
            -1 if r does not appear in the CSS file in rule i or later
            the largest j >= i where r appears in rule j of the file
        :throws:
            IndexError if i out of range
        """
        if i < 0 or i >= len(self.cliques):
            raise IndexError

        s = r.getSelector()
        p = r.getProperty()

        for j in xrange(len(self.cliques) - 1, i - 1, -1):
            (ss, pp) = self.cliques[j]
            if s in ss and p in pp:
                return j

        return -1

    def first_index_of(self, rSet, i = 0):
        """
        :param rSet:
            A set of simpleRule
        :param i:
            An index in range(self.num_rules())
        :returns:
            -1 if r does not appear in the CSS file in rule i or later
            the smallest j >= i where r appears in rule j of the file
        :throws:
            IndexError if i out of range
        """
        if i < 0 or i >= len(self.cliques):
            raise IndexError


        for j in xrange(i,len(self.cliques)):
            (ss, pp) = self.cliques[j]
            for r in rSet:
                s = r.getSelector()
                p = r.getProperty()
                if s in ss and p in pp:
                    return j

        return -1

    #def add_simple_rule(self, r, i=0):
    def add_simple_rule(self, r1, r2, colored_edges):
        """
        :param r1:
            A simpleRule
        :param r2:
            A simpleRule
        :param colored_edges:
            edges (as pairs) appearing in edgeOrder from original CSS
        :returns:
            None. It assumes that r1 does not appear already in cliques.
            It assumes that r2 appears in cliques. It adds r to the first
            position where r2 appears and does not *add* edges in colored_edges
            when r1 is added.
        """

        s1 = r1.getSelector()
        p1 = r1.getProperty()
        s2 = r2.getSelector()
        p2 = r2.getProperty()

        for j in xrange(len(self.cliques)):
            (ss, pp) = self.cliques[j]
            # Case when both s1 and p1 already in cliques
            if s1 in ss and p1 in pp:
                good = True
                break
            if s2 in ss and p2 in pp:
                good = True
                for s3 in ss:
                    if p1 not in pp and (s3,p1) in colored_edges:
                        good = False
                        break
                if good:
                    for p3 in pp:
                        if s1 not in ss and (s1,p3) in colored_edges:
                            good = False
                            break
                if good:
                    ss.add(s1)
                    if not p1 in pp:
                        pp.append(p1)
                    break

        assert good, "Something wrong at the end of add_simple_rule"
        #return j
                    #return j
#
        #(ss, pp) = self.cliques[i]
        #ss.add(s)
        #if p not in pp:
            #pp.append(p)

    def add_rules(self, cliques):
        """Adds the given list of rules (cliques) to the end of the CSS
        :param cliques:
            A list of pairs (ss, ps) where ss is a set of selectors in the same format as simpleRule
            selectors and ps is a set of properties in the same format as simpleRule
        """
        self.cliques.extend(cliques)

    def concat(self, other):
        """ Add all buckets of other to the end of self
        :param other:
            A cliqueCSS object
        """
        self.add_rules(other.cliques)
        prop_names.update(other.prop_names)

    def get_edge_set(self):
        """Note: computes each time

        :returns a set of all simpleRules covered by the cliqueCSS:
        """
        return { simpleRule(s, p) for (ss, pp) in self.cliques
                                  for (s, p) in product(ss, pp) }

    def is_sub_css(self, css):
        """
        :param css:
            A simple CSS object
        :returns:
            True iff the object represents a CSS file that contains a subset of
            the edges of CSS and respects the order
        """
        edgeSet = self.get_edge_set()

        if not edgeSet <= css.edgeSet:
            if __DEBUG__:
                print 'There are ' + str(len(edgeSet)) +' edges in edgeSet'
                print 'There are ' + str(len(css.edgeSet)) +\
                        ' edges in css.edgeSet'
                print 'There are ' + str(len(edgeSet - css.edgeSet)) +\
                        ' edges in edgeSet - css.edgeSet'
                print 'There are ' + str(len(css.edgeSet - edgeSet)) +\
                        ' edges in css.edgeSet - edgeSet'
                print 'Edges missing from simple css: ' +\
                        str(edgeSet - css.edgeSet)
            return False

        return self.__edge_order_respected(css.edgeOrder)

    def is_super_css(self, css):
        """
        :param css:
            A simple CSS object
        :returns:
            True iff the object represents a CSS file that contains a superset of
            the edges of CSS and respects the order
        """
        edgeSet = self.get_edge_set()

        if not css.edgeSet <= edgeSet:
            if __DEBUG__:
                print 'There are ' + str(len(edgeSet)) +' edges in edgeSet'
                print 'There are ' + str(len(css.edgeSet)) +\
                        ' edges in css.edgeSet'
                print 'There are ' + str(len(edgeSet - css.edgeSet)) +\
                        ' edges in edgeSet - css.edgeSet'
                print 'There are ' + str(len(css.edgeSet - edgeSet)) +\
                        ' edges in css.edgeSet - edgeSet'
                print 'Edges missing from clique css: ' +\
                        str(css.edgeSet - edgeSet)
            return False

        return self.__edge_order_respected(css.edgeOrder)

    def __edge_order_respected(self, edgeOrder):
        """
        :param edgeOrder:
            A list of pairs of simpleRules (e1, e2) giving order e1 < e2
        :returns:
            True iff the cliqueCSS object respects the edgeOrder
        """
        last_occurence = dict()
        i = 0
        for (ss, pp) in self.cliques:
            for s in ss:
                for p in pp:
                    e = simpleRule(s, p)
                    last_occurence[e] = i
                    i += 1

        for (e1, e2) in edgeOrder:
            if (e1 in last_occurence and
                e2 in last_occurence and
                not last_occurence[e1] < last_occurence[e2]):
                print "Edge ", e1, " last appears at property position", last_occurence[e1]
                print "Edge ", e2, " last appears at property position", last_occurence[e2]
                print "But the first should appear before the second!"
                return False

        return True


    def equivalent(self, css):
        """
        :param css:
            A simple CSS object
        :returns:
            True iff the object represents the same CSS file as css.
            That is, contains the same edges and respects the order.
        """
        edgeSet = { simpleRule(s, p)
                    for (ss, pp) in self.cliques
                    for (s, p) in product(ss, pp) }

        if edgeSet != css.edgeSet:
            if __DEBUG__:
                print 'There are ' + str(len(edgeSet)) +' edges in edgeSet'
                print 'There are ' + str(len(css.edgeSet)) +\
                        ' edges in css.edgeSet'
                print 'There are ' + str(len(edgeSet - css.edgeSet)) +\
                        ' edges in edgeSet - css.edgeSet'
                print 'There are ' + str(len(css.edgeSet - edgeSet)) +\
                        ' edges in css.edgeSet - edgeSet'
                print 'Edges missing from clique: ' +\
                        str(css.edgeSet - edgeSet)
                print 'Edges missing from simple css: ' +\
                        str(edgeSet - css.edgeSet)
            return False

        last_occurence = dict()
        i = 0
        lo_to_bucket = dict()
        j = 0
        for (ss, pp) in self.cliques:
            for s in ss:
                for p in pp:
                    e = simpleRule(s, p)
                    last_occurence[e] = i
                    lo_to_bucket[i] = j
                    i += 1
            j += 1

        for (e1, e2) in css.edgeOrder:
            # TODO: fix so edges can be in same bucket as long as they can be
            # ordered
            if not last_occurence[e1] < last_occurence[e2]:
                print "Edge ", e1, " last appears at property position", last_occurence[e1]
                print "Edge ", e1, " last appears at bucket", \
                lo_to_bucket[last_occurence[e1]]
                print self.cliques[lo_to_bucket[last_occurence[e1]]]
                print "Edge ", e2, " last appears at property position", last_occurence[e2]
                print "Edge ", e2, " last appears at bucket", \
                lo_to_bucket[last_occurence[e2]]
                print self.cliques[lo_to_bucket[last_occurence[e2]]]
                print "But the first should appear before the second!"
                return False

        return True

    def equivalent_masked(self, css):
        """
        :param css:
            A simple CSS object
        :returns:
            True iff the object represents the same CSS file as css if property masking is taken into account.
            E.g. s {p: 1; p: 2} has p: 1 masked so not counted.
            Requires prop_names to have been given.
        """

        edgeSet = set()
        pnEdgeSet = set()

        for (ss, pp) in reversed(self.cliques):
            for s in ss:
                for p in reversed(pp):
                    pn = self.prop_names[p]
                    if (s, pn) not in pnEdgeSet:
                        pnEdgeSet.add((s, pn))
                        edgeSet.add(simpleRule(s, p))

        simple_trcl = css.getTrClEdgeOrder()
        simple_masked = { r1
                          for (r1, r2) in css.getTrClEdgeOrder()
                          if ((r1.getSelector() == r2.getSelector())
                              and
                              (self.prop_names[r1.getProperty()] ==
                               self.prop_names[r2.getProperty()])) }

        cssEdgeSet = css.edgeSet - simple_masked

        if edgeSet != cssEdgeSet:
            if __DEBUG__:
                print 'There are ' + str(len(edgeSet)) +' edges in edgeSet'
                print 'There are ' + str(len(cssEdgeSet)) +\
                        ' edges in cssEdgeSet'
                print 'There are ' + str(len(edgeSet - cssEdgeSet)) +\
                        ' edges in edgeSet - cssEdgeSet'
                print 'There are ' + str(len(cssEdgeSet - edgeSet)) +\
                        ' edges in cssEdgeSet - edgeSet'
                print 'Edges missing from clique: ' +\
                        str(cssEdgeSet - edgeSet)
                print 'Edges missing from simple css: ' +\
                        str(edgeSet - cssEdgeSet)
            return False

        last_occurence = dict()
        i = 0
        lo_to_bucket = dict()
        j = 0
        for (ss, pp) in self.cliques:
            for s in ss:
                for p in pp:
                    e = simpleRule(s, p)
                    last_occurence[e] = i
                    lo_to_bucket[i] = j
                    i += 1
            j += 1

        for (e1, e2) in css.edgeOrder:
            if e1 in cssEdgeSet and e2 in cssEdgeSet:
                # TODO: fix so edges can be in same bucket as long as they can be
                # ordered
                if not last_occurence[e1] < last_occurence[e2]:
                    print "Edge ", e1, " last appears at property position", last_occurence[e1]
                    print "Edge ", e1, " last appears at bucket", \
                    lo_to_bucket[last_occurence[e1]]
                    print self.cliques[lo_to_bucket[last_occurence[e1]]]
                    print "Edge ", e2, " last appears at property position", last_occurence[e2]
                    print "Edge ", e2, " last appears at bucket", \
                    lo_to_bucket[last_occurence[e2]]
                    print self.cliques[lo_to_bucket[last_occurence[e2]]]
                    print "But the first should appear before the second!"
                    return False

        return True


    def no_conflicts(self, conflicts):
        """
        :param conflicts:
            A set of pairs (e1, e2) of simpleRules
        :returns:
            True iff no (e1, e2) in conflicts has e1 and e2 in the same bucket
        """
        for (e1, e2) in conflicts:
            for (ss, pp) in self.cliques:
                if (e1.getSelector() in ss and
                    e2.getSelector() in ss and
                    e1.getProperty() in pp and
                    e2.getProperty() in pp):
                    return False
        return True

    def __str__(self):
        bits = ["\n"]
        counter = 0
        for (ss, pp) in self.cliques:
            bits.append("/* Rule number " + str(counter) + " */\n")
            bits.append(",\n".join(ss))
            bits.append(" {\n    ")
            #print pp
            bits.append(";\n    ".join(pp))
            bits.append("\n}\n\n")

        return ''.join(bits)

    def __repr__(self):
        return "Id: " + repr(id(self)) + "\n" + str(self)

    def __iter__(self):
        """Iterates over pairs (ss, pp) of a set of selectors and properties
        in same format as in simpleRule"""
        return iter(self.cliques)

def main():
    r1 = simpleRule('A','1')
    r2 = simpleRule('A','4')
    r3 = simpleRule('A','7')
    r4 = simpleRule('B','1')
    r5 = simpleRule('B','4')
    r6 = simpleRule('C','4')
    r7 = simpleRule('C','5')
    r8 = simpleRule('C','7')
    r9 = simpleRule('D','3')
    r10 = simpleRule('D','5')
    r11 = simpleRule('D','6')
    r12 = simpleRule('E','2')
    r13 = simpleRule('E','3')
    r14 = simpleRule('E','6')
    r15 = simpleRule('E','7')
    r16 = simpleRule('F','2')
    r17 = simpleRule('F','7')
    CSS = simpleCSS([ eval('r'+str(i)) for i in range(1,18)],[(r1,r2),(r2,r3)])
    clique = cliqueCSS()
    clique.add_rule({r1.getSelector()},[r1.getProperty()])
    clique.add_rule({r3.getSelector()},[r3.getProperty()])
    clique.add_rule({r2.getSelector()},[r2.getProperty()])
    assert clique.is_sub_css(CSS), 'something wrong'

if __name__ == '__main__':
        main()
