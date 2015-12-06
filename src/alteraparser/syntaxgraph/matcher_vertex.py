from .vertex import Vertex, VertexCategory


class MatcherVertex(Vertex):

    def __init__(self, chars=[], negated=False):
        Vertex.__init__(self, VertexCategory.MATCHER)
        self.__chars = set(chars)
        self.__negated = negated

    def matches(self, ch):
        if not self.__negated:
            return ch in self.__chars
        else:
            return ch not in self.__chars

    def negate(self, neg=True):
        self.__negated = neg
        return self

    def add(self, ch):
        self.__chars.append(ch)
        return self

    def _on_clone_creation(self, original):
        Vertex._on_clone_creation(self, original)
        self.__chars = set(original.__chars)
        self.__negated = original.__negated

    def __str__(self):
        chars = '[' + ','.join(self.__chars) + ']'
        if self.__negated:
            return 'MATCH: NOT {}'.format(chars)
        else:
            return 'MATCH: {}'.format(chars)


