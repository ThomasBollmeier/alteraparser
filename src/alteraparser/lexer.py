import re
from typing import Optional

from alteraparser.token_ import Token, TokenStream
from alteraparser.lexer_grammar import LexerGrammar

class Lexer(TokenStream):

    def __init__(self, grammar: LexerGrammar, text: str=""):
        self.grammar = grammar
        self.input = text
        self.line = 1
        self.column = 1

    def set_input(self, text: str):
        self.input = text
        self.line = 1
        self.column = 1

    def advance(self) -> Optional[Token]:
        if not self.input:
            return None
        while self.input:
            ignored = False
            for token_type, regex, ignore in self.grammar.get_rules():
                match = regex.match(self.input)
                if match:
                    value = match.group(0)
                    token = Token(token_type, value, self.line, self.column)
                    lines = value.split('\n')
                    if len(lines) > 1:
                        self.line += len(lines) - 1
                        self.column = len(lines[-1]) + 1
                    else:
                        self.column += len(value)
                    self.input = self.input[len(value):]
                    if ignore:
                        ignored = True
                        break
                    return token
            if ignored:
                continue
            raise SyntaxError(f'Unexpected token at line {self.line}, column {self.column}')
        return None
