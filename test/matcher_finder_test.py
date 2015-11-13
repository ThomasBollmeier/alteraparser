import unittest

from alteraparser import char_range, fork, many, single_char, keyword, \
    characters, one_to_many, optional, grammar
from alteraparser.io.string_input import StringInput
from alteraparser.syntaxgraph.match_finder import MatchFinder


class MatchFinderTest(unittest.TestCase):

    def setUp(self):
        alpha = char_range('a', 'z')
        num = char_range('0', '9')
        alpha_num = fork([alpha], [num])
        dash = fork([single_char('-')]).set_name('sep')
        self.grammar = grammar('var', [
            fork([
                alpha,
                many(fork(
                    [alpha_num],
                    [dash, alpha_num]))])])

    def tearDown(self):
        pass

    def test_match(self):
        data_in = StringInput('this-is-a-test')
        finder = MatchFinder(data_in)
        self.grammar.get_dock_vertex().walk(finder)
        act = self._path_repr(finder.path)
        exp = '<var>this<sep>-</sep>is<sep>-</sep>a<sep>-</sep>test</var>'
        self.assertEqual(exp, act)

        data_in = StringInput('not-allowed-')
        finder = MatchFinder(data_in)
        self.grammar.get_dock_vertex().walk(finder)
        act = self._path_repr(finder.path)
        exp = ''
        self.assertEqual(exp, act)

    def test_keyword_match(self):
        wspace = one_to_many(characters(' ', '\t', '\n')).set_name('ws').set_ignore()
        alpha = char_range('a', 'z')
        num = char_range('0', '9')
        alpha_num = fork([alpha], [num])
        dash = single_char('-')
        brace_open = single_char('{')
        brace_close = single_char('}')
        var_name = fork([alpha,
                        many(fork([alpha_num],
                                  [dash, alpha_num]))]).set_name('name')
        class_ = keyword('CLASS')
        class_expr = fork([class_,
                           wspace,
                           var_name,
                           wspace,
                           brace_open,
                           optional(wspace),
                           brace_close])
        class_grammar = grammar('class', [class_expr])

        code = 'CLASS  my-test {\n}'
        finder = MatchFinder(StringInput(code))
        class_grammar.get_dock_vertex().walk(finder)

        exp = '<class><key>CLASS</key><name>my-test</name>{}</class>'
        act = self._path_repr(finder.path)
        self.assertEqual(exp, act)


    @staticmethod
    def _path_repr(path):
        res = ''
        ignore_mode = False
        for vertex, ch in path:
            if vertex.is_group_start():
                if vertex.ignore:
                    ignore_mode = True
                elif vertex.name:
                    res += '<' + vertex.name + '>'
            elif vertex.is_group_end():
                if vertex.ignore:
                    ignore_mode = False
                elif vertex.name:
                    res += '</' + vertex.name + '>'
            if ch is not None and not ignore_mode:
                res += ch
        return res


if __name__ == '__main__':

    unittest.main()

