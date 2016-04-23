import unittest
from alteraparser.parser import Parser, ParseError
from alteraparser.bnf.grammar import *


class BnfGrammarTest(unittest.TestCase):

    def setUp(self):
        self.parser = Parser(bnf_grammar)

    def test_rules(self):
        code = """
            -- Configuration:

            set config.case_sensitive on;

            -- Tokens:

            WHITESPACE = <space> | <tab> | <newline>;

            DUMMY = [^?]?;

            ALPHA = 'a'..'z' | 'A'..'Z';

            ALPHA_NUM = ALPHA | '0'..'9';

            VAR_NAME = ALPHA & (ALPHA_NUM | '-' & ALPHA_NUM)&*;

            -- Production rules:

            block_comment = '/*'  &? ( [^*] | '*' & [^/] )&+ &? '*/';

            line_comment = ';;' &? [^<newline>]&* &? <newline>;

            call = '(' &? expr#callee expr#arg* &? ')';

            @grammar
            my_lisp = WHITESPACE? call+ WHITESPACE?;
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
