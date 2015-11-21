from alteraparser.syntaxgraph.matcher_vertex import MatcherVertex
from alteraparser.syntaxgraph.final_vertex import FinalVertex
from alteraparser.syntaxgraph.vertex_group import Multiples, Branches, VertexGroup


def group(name=None, is_unique=False, transform_ast_fn=None):
    def init(self):
        VertexGroup.__init__(self)
        if name:
            self._VertexGroup__start.name = name
            self._VertexGroup__end.name = name
        self._VertexGroup__end.is_rule_end = is_unique
        if transform_ast_fn:
            self._VertexGroup__end.transform_ast_fn = transform_ast_fn

    def factory(on_expand_fn):
        return type(on_expand_fn.__name__,
                    (VertexGroup,),
                    {'__init__': init,
                     '_on_expand': on_expand_fn})
    return factory


def optional(element):
    return Multiples(element, max_occur=1)


def many(element):
    return Multiples(element)


def one_to_many(element):
    return Multiples(element, min_occur=1)


def fork(*branches):
    res = Branches()
    for branch in branches:
        if isinstance(branch, list):
            res.add_branch(branch)
        else:
            res.add_branch([branch])
    return res


def seq(sep, *elements):
    new_elements = []
    for el in elements:
        if new_elements:
            new_elements.append(sep)
        new_elements.append(el)
    return fork(new_elements)


def grammar(name, branches, transform_ast_fn=None):
    res = fork(*branches).set_name(name)
    if transform_ast_fn:
        res = res.transform_ast(transform_ast_fn)
    res.connect(FinalVertex())
    return res


def single_char(ch):
    return MatcherVertex([ch])


def char_range(ch_from, ch_to):
    return MatcherVertex([chr(i) for i in range(ord(ch_from), ord(ch_to) + 1)])


def characters(*chars):
    return MatcherVertex(chars)


def keyword(kw, case_sensitive=True, name='key'):
    branch = []
    if case_sensitive:
        for ch in kw:
            branch.append(single_char(ch))
    else:
        for ch in kw:
            elem = fork([single_char(ch.lower())],
                        [single_char(ch.upper())])
            branch.append(elem)
    return fork(branch).set_name(name)


def token(element, name='token'):
    return fork(element).set_name(name)
