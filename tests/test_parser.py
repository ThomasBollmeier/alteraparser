from alteraparser.ast_ import AstStrWriter
from alteraparser.parser import Parser
from alteraparser.token_ import Token, TokenStreamFromList
from tests.grammar4test import *

def test_simple_expr():
    # Example token sequence for the expression: (3 + 5) * x
    _run_parser([
        Token(LPAREN, '(', 1, 1),
        Token(NUMBER, '3', 1, 2),
        Token(PLUS, '+', 1, 4),
        Token(NUMBER, '5', 1, 6),
        Token(RPAREN, ')', 1, 7),
        Token(MULTIPLY, '*', 1, 9),
        Token(IDENT, 'x', 1, 11)
    ])

def test_call_expr():
    # Example token sequence for the expression: foo(42, bar)
    _run_parser([
        Token(IDENT, 'foo', 1, 1),
        Token(LPAREN, '(', 1, 4),
        Token(NUMBER, '42', 1, 5),
        Token(COMMA, ',', 1, 7),
        Token(IDENT, 'bar', 1, 9),
        Token(RPAREN, ')', 1, 12)
    ])

def _run_parser(tokens):
    parser = Parser(make_grammar_for_test())
    try:
        ast = parser.parse(TokenStreamFromList(tokens))
        print("Parse successful! Matched path:")
        writer = AstStrWriter()
        ast_str = writer.write_ast_to_str(ast)
        print(ast_str)
    except SyntaxError as e:
        print(f"Parse error: {e}")

