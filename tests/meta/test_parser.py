from alteraparser.meta.lexer_grammar import LexerGrammar
from alteraparser.meta.grammar import create_meta_grammar
from alteraparser.parser import TextParser
from alteraparser.ast_ import AstStrWriter


def test_parser():
    lg = LexerGrammar()
    g = create_meta_grammar()
    parser = TextParser(g, lg)

    source = """
        -- Class Declaration
        class_decl -> CLASS name#IDENTIFIER LBRACE 
            attrs_decl
            methods_decl
            RBRACE;
        attrs_decl -> ATTRS LBRACE 
            (ATTR attr#IDENTIFIER)+
        RBRACE;
        methods_decl -> METHODS LBRACE
            (METHOD method#IDENTIFIER LPAREN RPAREN)+
        RBRACE; 
        """

    ast = parser.parse_text(source)

    assert ast is not None

    writer = AstStrWriter(indent_size=4)
    print(writer.write_ast_to_str(ast))