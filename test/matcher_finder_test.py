import unittest
from alteraparser.io.string_input import StringInput
from alteraparser.syntaxgraph.match_finder import MatchFinder
from alteraparser.syntaxgraph.vertex_group import optional, one_to_many, many, fork
from alteraparser.syntaxgraph.vertex import VertexCategory
from alteraparser.syntaxgraph.matcher_vertex import single_char, char_range, characters


class MatchFinderTest(unittest.TestCase):

    def setUp(self):
        alpha = char_range('a', 'z')
        num = char_range('0', '9')
        alpha_num = fork([alpha], [num])
        dash = fork([single_char('-')]).set_name('sep')
        self.grammar = fork([alpha,
                             many(fork(
                                 [alpha_num],
                                 [dash, alpha_num]))]).set_name('var')

    def tearDown(self):
        pass

    def test_match(self):
        data_in = StringInput('this-is-a-test')
        finder = MatchFinder(data_in)
        self.grammar.get_dock_vertex().walk(finder)
        act = self._path_repr(finder.path)
        exp = '<var>this<sep>-</sep>is<sep>-</sep>a<sep>-</sep>test</var>'
        self.assertEqual(act, exp)

    @staticmethod
    def _path_repr(path):
        res = ''
        stack = []
        for vertex, ch in path:
            catg = vertex.get_category()
            if catg == VertexCategory.GROUP_START:
                if vertex.name:
                    res += '<' + vertex.name + '>'
                stack.append(vertex.name)
            elif catg == VertexCategory.GROUP_END and stack:
                name = stack.pop()
                if name:
                    res += '</' + name + '>'
            if ch is not None:
                res += ch
        return res


if __name__ == '__main__':

    unittest.main()

