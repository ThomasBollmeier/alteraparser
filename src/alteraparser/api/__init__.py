from alteraparser.syntaxgraph.matcher_vertex import MatcherVertex
from alteraparser.syntaxgraph.final_vertex import FinalVertex
from alteraparser.syntaxgraph.vertex_group import Multiples, Branches


def optional(element):
    return Multiples(element, max_occur=1)


def many(element):
    return Multiples(element)


def one_to_many(element):
    return Multiples(element, min_occur=1)


def fork(*branches):
    res = Branches()
    for branch in branches:
        res.add_branch(branch)
    return res


def grammar(*branches):
    res = fork(*branches)
    res.connect(FinalVertex())
    return res


def single_char(ch):
    return MatcherVertex([ch])


def char_range(ch_from, ch_to):
    return MatcherVertex([chr(i) for i in range(ord(ch_from), ord(ch_to) + 1)])


def characters(*chars):
    return MatcherVertex(chars)


def keyword(kw, case_sensitive=True):
    branch = []
    if case_sensitive:
        for ch in kw:
            branch.append(single_char(ch))
    else:
        for ch in kw:
            elem = fork([single_char(ch.lower())],
                        [single_char(ch.upper())])
            branch.append(elem)
    return fork(branch)


