from alteraparser.meta.lexer_grammar import LexerGrammar
from alteraparser.lexer import Lexer

def test_lexer():
    lg = LexerGrammar()
    lexer = Lexer(lg)

    source = """
    -- Class Declaration
    class_decl -> 'class' name#IDENTIFIER block< 
        attr_decl+
        >;
    attr_decl -> 'attr' name#IDENTIFIER; 
    block<body> -> LBRACE body RBRACE | 'begin' body 'end';
    """
    lexer.set_input(source)

    while True:
        token = lexer.advance()
        if token is None:
            break
        print(f"{token}")


