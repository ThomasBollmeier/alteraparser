import unittest
from alteraparser.parser import Parser, ParseError
from alteraparser.bnf.grammar import *


class BnfGrammarTest(unittest.TestCase):

    def setUp(self):
        self.parser = Parser(bnf_grammar)

    def test_rules(self):
        code = """
            WHITESPACE = <space> | <tab> | <newline>;

            alpha = 'a'..'z' | 'A'..'Z';

            alpha_num = alpha | '0'..'9';

            var_name = alpha & (alpha_num | '-' & alpha_num)&*;

            block_comment = '/*'  &? ( [^*] | '*' & [^/] )&+ &? '*/';

            line_comment = ';;' &? [^<newline>]&* &? <newline>;

            call = '(' &? expr#callee expr#arg* &? ')';

            @grammar
            my_lisp = call+;
        """
        ast = self.parser.parse_string(code)
        self.assertIsNotNone(ast)
        print(ast.to_xml())

        code_with_errors = """
            alpha = 'a'..'z' | 'A'..'Z';
            alpha_num = alpha | '0'..'9';
            varname = alpha ( alpha_num | '-' alpha_num )*
        """
        self.assertRaises(ParseError, self.parser.parse_string, code_with_errors)

if __name__ == '__main__':

    unittest.main()