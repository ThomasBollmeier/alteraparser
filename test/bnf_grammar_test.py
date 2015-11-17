import unittest
from alteraparser.parser import Parser
from alteraparser.bnf.grammar import *


class BnfGrammarTest(unittest.TestCase):

    def setUp(self):
        self.parser = Parser(bnf_grammar)

    def test_rules(self):
        code = """
            alpha = 'a'..'z' | 'A'..'Z';
            alpha_num = alpha | '0'..'9';
            ws = <newline> | <tab> | <space>;
            varname = alpha | ( alpha_num | '-' alpha_num )*;
        """
        ast = self.parser.parse_string(code)
        self.assertIsNotNone(ast)

if __name__ == '__main__':

    unittest.main()