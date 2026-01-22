from alteraparser.lexer_grammar import LexerGrammar
from alteraparser.grammar import *
from alteraparser.ast_ import Ast

def make_lexer_grammar_for_test() -> LexerGrammar:
    lg = LexerGrammar()
    lg.add_rule("WHITESPACE", r'\s+', ignore=True)
    lg.add_rule("COMMENT", r'//.*', ignore=True)
    lg.add_rule("NUMBER", r'\d+')
    lg.add_rule("IDENT", r'[a-zA-Z_][a-zA-Z0-9_]*')
    lg.add_rule("PLUS", r'\+')
    lg.add_rule("MINUS", r'-')
    lg.add_rule("MULTIPLY", r'\*')
    lg.add_rule("DIVIDE", r'/')
    lg.add_rule("LPAREN", r'\(')
    lg.add_rule("RPAREN", r'\)')
    lg.add_rule("COMMA", r',')
    return lg


# Grammar definition
def make_grammar_for_test() -> Grammar:
    grammar = Grammar()
    lg = make_lexer_grammar_for_test()

    def _trans_single_child(ast: Ast) -> Ast:
        if len(ast.children) == 1:
            return ast[0]
        return ast

    @rule(grammar, "sum", is_start_rule=True)
    def _sum(g):
        rest = many(seq(choice(tok(lg.PLUS), tok(lg.MINUS)), g.term))
        return seq(g.term, rest)

    @rule(grammar, "term")
    def _term(g):
        rest = many(seq(choice(tok(lg.MULTIPLY), tok(lg.DIVIDE)), g.factor))
        return seq(g.factor, rest)

    @rule(grammar, "factor")
    def _factor(g):
        num = tok(lg.NUMBER)
        ident = tok(lg.IDENT)
        return choice(num, ident, g.group, g.call)

    @rule(grammar, "group")
    def _group(g):
        return seq(tok(lg.LPAREN), g.sum, tok(lg.RPAREN))

    @ast_transformer(grammar, "group")
    def _trans_group(ast: Ast) -> Ast:
        return ast[1]

    @rule(grammar, "call")
    def _call(g):
        args = opt(seq(g.sum.set_id("arg"), many(seq(tok(lg.COMMA), g.sum.set_id("arg")))))
        return seq(tok(lg.IDENT, "callee"), tok(lg.LPAREN), args, tok(lg.RPAREN))

    @ast_transformer(grammar, "call")
    def _trans_call(ast: Ast) -> Ast:
        call_ast = Ast(name="call")

        callee = ast.get_child_by_id("callee").value
        call_ast.add_child(Ast(name="callee", value=callee))

        args_ast = Ast(name="arguments")
        call_ast.add_child(args_ast)
        args = ast.get_children_by_id("arg")
        for arg in args:
            args_ast.add_child(arg)

        return call_ast

    grammar.add_ast_transformer("sum", _trans_single_child)
    grammar.add_ast_transformer("term", _trans_single_child)
    grammar.add_ast_transformer("factor", _trans_single_child)

    return grammar