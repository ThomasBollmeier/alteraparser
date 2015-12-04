import unittest
from alteraparser.io.string_input import StringInput
from alteraparser.io.output import ConsoleOutput
from alteraparser.codegen.generator import Generator
from alteraparser.bnf.grammar import *


class GeneratorTest(unittest.TestCase):

    def setUp(self):
        self.generator = Generator(ConsoleOutput())

    def test_rules(self):
        code = """
            WHITESPACE = <space> | <tab> | <newline>;

            alpha = 'a'..'z' | 'A'..'Z';

            alpha_num = alpha | '0'..'9';

            var_name = alpha & (alpha_num | '-' & alpha_num)&*;

            no_special = [^*?!];

            block_comment = '/*'  &? ( [^*] | '*' & [^/] )&+ &? '*/';

            line_comment = ';;' &? [^<newline>]&* &? <newline>;

            @unique
            call = '(' &? expr#callee expr#arg* &? ')';

            @grammar
            my_lisp = call+;
        """
        self.generator.generate_parser(StringInput(code))

if __name__ == '__main__':

    unittest.main()