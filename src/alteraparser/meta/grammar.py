from alteraparser.grammar import *
from alteraparser.meta.lexer_grammar import LexerGrammar as MetaLexerGrammar

def create_meta_grammar() -> Grammar:
    grammar = Grammar()
    lg = MetaLexerGrammar()

    @rule(grammar, "rule_defs", is_start_rule=True)
    def _rule_defs(g):
        return one_or_more(g.rule_def)

    @rule(grammar, "rule_def")
    def _rule_def(g):
        return seq(
            tok(lg.IDENT, "rule_def"),
            tok(lg.ARROW),
            g.rhs.set_id("rhs"),
            tok(lg.SEMICOLON)
        )
    @ast_transformer(grammar, "rule_def")
    def _transform_rule_def(ast):
        rule_name = ast.get_child_by_id("rule_def").value
        new_ast = Ast("rule_def")
        new_ast.set_attr("name", rule_name)
        for child in ast.get_children_by_id("rhs"):
            new_ast.add_child(child)
        return new_ast


    @rule(grammar, "rhs")
    def _rhs(g):
        return seq(
            g.branch.set_id("branch"),
            many(seq(tok(lg.PIPE), g.branch.set_id("branch")))
        )
    @ast_transformer(grammar, "rhs")
    def _transform_rhs(ast):
        branches = ast.get_children_by_id("branch")
        if len(branches) == 1:
            return branches[0]
        new_ast = Ast("branches")
        for branch in branches:
            new_ast.add_child(branch)
        return new_ast


    @rule(grammar, "branch")
    def _branch(g):
        return one_or_more(g.item)
    @ast_transformer(grammar, "branch")
    def _transform_branch(ast):
        items = ast.get_children()
        if len(items) == 1:
            item = items[0]
            item.id = ""
            return item
        new_ast = Ast("sequence")
        for item in items:
            item.id = ""
            new_ast.add_child(item)
        return new_ast

    @rule(grammar, "item")
    def _item(g):
        return seq(
            g.element,
            opt(g.multiplier)
        )
    @ast_transformer(grammar, "item")
    def _transform_item(ast):
        children = ast.get_children()
        ret = children[0]
        ret.id = ""
        if len(children) == 2:
            multiplier = children[1].children[0].value
            ret.set_attr("multiplier", multiplier)
        return ret

    @rule(grammar, "element")
    def _element(g):
        return choice(
            g.atom,
            seq(tok(lg.LPAREN), g.branch, tok(lg.RPAREN)),
        )
    @ast_transformer(grammar, "element")
    def _transform_element(ast):
        children = ast.get_children()
        if len(children) == 1:
            return children[0]
        else:
            return children[1]

    @rule(grammar, "atom")
    def _atom(_):
        return seq(
            opt(seq(tok(lg.IDENT, "id"), tok(lg.HASH))),
            choice(
                tok(lg.TOKEN_TYPE, "token_type"),
                tok(lg.IDENT, "rule"),
            )
        )
    @ast_transformer(grammar, "atom")
    def _transform_atom(ast):
        id_ast = ast.get_child_by_id("id")
        token_type_ast = ast.get_child_by_id("token_type")
        if token_type_ast:
            ret = Ast("token_type", token_type_ast.value)
        else:
            rule_ast = ast.get_child_by_id("rule")
            ret = Ast("rule", rule_ast.value)
        ret.id = ""
        if id_ast:
            ret.set_attr("identifier", id_ast.value)
        return ret

    @rule(grammar, "multiplier")
    def _multiplier(_):
        return choice(
            tok(lg.QUESTION_MARK),
            tok(lg.STAR),
            tok(lg.PLUS)
        )

    return grammar