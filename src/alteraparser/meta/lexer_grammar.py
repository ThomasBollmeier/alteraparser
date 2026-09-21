from alteraparser.lexer_grammar import LexerGrammar as AlteraLexerGrammar

class LexerGrammar(AlteraLexerGrammar):

    def __init__(self):
        AlteraLexerGrammar.__init__(self)

        self.add_rule("WHITESPACE", r'\s+', ignore=True)
        self.add_rule("COMMENT", r'--.*', ignore=True)
        self.add_rule("TOKEN_TYPE", r'[A-Z][A-Z0-9_]*')
        self.add_rule("IDENT", r'[a-z][a-z0-9_]*')
        self.add_rule("ARROW", r'->')
        self.add_rule("SEMICOLON", r';')
        self.add_rule("QUESTION_MARK", r'\?')
        self.add_rule("STAR", r'\*')
        self.add_rule("PLUS", r'\+')
        self.add_rule("PIPE", r'\|')
        self.add_rule("LPAREN", r'\(')
        self.add_rule("RPAREN", r'\)')
        self.add_rule("HASH", r'#')

