from alteraparser.parser import Parser
from alteraparser.bnf.grammar import bnf_grammar


class Generator(object):

    def __init__(self):
        self.__bnf_parser = Parser(bnf_grammar)

    def generate_parser(self, grammar_input_stream, output):
        ast = self.__bnf_parser