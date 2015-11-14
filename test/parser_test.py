import unittest
from alteraparser import grammar, keyword, single_char, token, \
    char_range, characters, seq, fork, many, one_to_many, optional
from alteraparser.parser import Parser
from alteraparser.ast import AST


class ParserTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_parse_string(self):
        test_grammar = self.__create_grammar()
        parser = Parser(test_grammar)
        code = 'LOOP AT people INTO person. ENDLOOP.'
        ast = parser.parse_string(code)
        self.assertIsNotNone(ast)
        self.assertEqual('people', ast['loop'][0]['#items'][0].text)
        self.assertEqual('person', ast['loop'][0]['#item'][0].text)
        self.assertEqual('LOOPATpeopleINTOperson.ENDLOOP.', ast.text)

    def test_parse_string_with_transform(self):
        test_grammar = self.__create_grammar(self.__transform_loop)
        parser = Parser(test_grammar)
        code = 'LOOP AT people INTO person. ENDLOOP.'
        ast = parser.parse_string(code)
        loop = ast['loop'][0]
        self.assertEqual('peopleperson', loop.text)
        self.assertEqual('people', loop['items'][0].text)
        self.assertEqual('person', loop['item'][0].text)


    def test_parse_file(self):
        test_grammar = self.__create_grammar()
        parser = Parser(test_grammar)
        ast = parser.parse_file('input.txt')
        self.assertIsNotNone(ast)
        self.assertEqual('people', ast['loop'][0]['#items'][0].text)
        self.assertEqual('person', ast['loop'][0]['#item'][0].text)

    def __create_grammar(self, transformer_fn = None):
        ALPHA = token(fork(char_range('a', 'z'), char_range('A', 'Z')))
        NUM = token(char_range('0', '9'))
        ALPHA_NUM = token(fork(ALPHA, NUM))
        UNDERSCORE = token(single_char('_'))
        DOT = token(single_char('.'))
        WS = token(one_to_many(characters(' ', '\t', '\n'))).set_ignore()

        loop = keyword('loop', False)
        endloop = keyword('endloop', False)
        at = keyword('at', False)
        into = keyword('into', False)

        varname = fork([ALPHA, many(fork(ALPHA_NUM, [UNDERSCORE, ALPHA_NUM]))]).set_name('var')
        items = varname.clone().set_id('items')
        item = varname.clone().set_id('item')

        loop_stmt = fork([seq(WS, loop, at, items, into, item), optional(WS), DOT, WS,
                          endloop, optional(WS), DOT]).set_name('loop')
        if transformer_fn:
            loop_stmt.transform_ast(transformer_fn)

        return grammar('test', loop_stmt)

    def __transform_loop(self, ast):
        items = ast['#items'][0]
        item = ast['#item'][0]
        res = AST('loop')
        res.add_child(AST('items', text=items.text))
        res.add_child(AST('item', text=item.text))
        return res


if __name__ == '__main__':

    unittest.main()
