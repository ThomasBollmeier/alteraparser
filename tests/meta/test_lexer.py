from alteraparser.meta.lexer_grammar import LexerGrammar
from alteraparser.lexer import Lexer

def test_lexer():
    lg = LexerGrammar()
    lexer = Lexer(lg)

    source = """
    -- Class Declaration
    class_decl -> 'class' name#IDENTIFIER LBRACE 
        attr_decl+
        RBRACE;
    attr_decl -> 'attr' name#IDENTIFIER; 
    """
    lexer.set_input(source)

    while True:
        token = lexer.advance()
        if token is None:
            break
        print(f"{token}")


