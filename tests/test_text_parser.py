from alteraparser.ast_ import AstStrWriter
from tests.grammar4test import make_lexer_grammar_for_test, make_grammar_for_test
from alteraparser.parser import TextParser

def make_text_parser_for_test():
    lexer_grammar = make_lexer_grammar_for_test()
    grammar = make_grammar_for_test()
    return TextParser(grammar, lexer_grammar)

def test_text_parser_simple_expr():
    parser = make_text_parser_for_test()

    input_text = """
        3 + 5 * x * y(42)
    """
    ast = parser.parse_text(input_text)

    assert ast is not None

    print("AST for simple expression:")
    ast_writer = AstStrWriter()
    print(ast_writer.write_ast_to_str(ast))