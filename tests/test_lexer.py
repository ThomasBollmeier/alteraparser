from tests.grammar4test import *
from alteraparser.lexer_grammar import LexerGrammar
from alteraparser.lexer import Lexer
from alteraparser.token_ import Token


def test_lexer_simple_expr():
    lg = make_lexer_grammar_for_test()
    lexer = Lexer(lg)
    lexer.set_input("(3 + 5) * x")

    expected_tokens = [
        Token(lg.LPAREN, '(', 1, 1),
        Token(lg.NUMBER, '3', 1, 2),
        Token(lg.PLUS, '+', 1, 4),
        Token(lg.NUMBER, '5', 1, 6),
        Token(lg.RPAREN, ')', 1, 7),
        Token(lg.MULTIPLY, '*', 1, 9),
        Token(lg.IDENT, 'x', 1, 11)
    ]

    for expected in expected_tokens:
        token = lexer.advance()
        assert token is not None
        assert token.token_type == expected.token_type
        assert token.value == expected.value
        assert token.line == expected.line
        assert token.column == expected.column

    assert lexer.advance() is None

def test_lexer_all_commented():
    lexer = Lexer(make_lexer_grammar_for_test())
    lexer.set_input("// This is a comment\n   // Another comment")

    assert lexer.advance() is None