from alteraparser.grammar import *
from alteraparser.meta.lexer_grammar import LexerGrammar as MetaLexerGrammar

def create_meta_grammar() -> Grammar:
    grammar = Grammar()
    lg = MetaLexerGrammar()

    @rule(grammar, "grammar", is_start_rule=True)
    def _grammar(g):
        return seq(
            g.token_type_defs,
            g.rule_defs,
        )

    @rule(grammar, "token_type_defs")
    def _token_type_defs(g):
        return seq(
            tok(lg.TOKENS),
            tok(lg.LBRACE),
            many(g.token_type_def.set_id("token_type_def")),
            tok(lg.RBRACE),
        )
    @ast_transformer(grammar, "token_type_defs")
    def _transform_token_type_defs(ast):
        ret = Ast("token_type_defs")
        for child in ast.get_children_by_id("token_type_def"):
            ret.add_child(child)
        return ret

    @rule(grammar, "token_type_def")
    def _token_type_def(_):
        return seq(
            tok(lg.TOKEN_TYPE),
            tok(lg.REGEX),
            opt(tok(lg.IGNORE)),
            tok(lg.SEMICOLON),
        )
    @ast_transformer(grammar, "token_type_def")
    def _transform_token_type_def(ast):
        name = ast[0].value
        regex = ast[1].value[6:-1] # regex(...)
        ignore = len(ast.get_children()) == 4
        ret = Ast("token_type_def")
        ret.set_attr("name", name)
        ret.set_attr("regex", regex)
        if ignore:
            ret.set_attr("ignore", "true")
        return ret

    @rule(grammar, "rule_defs")
    def _rule_defs(g):
        return one_or_more(g.rule_def)

    @rule(grammar, "rule_def")
    def _rule_def(g):
        return seq(
            tok(lg.IDENT, "name"),
            opt(seq(
                tok(lg.LBRACKET),
                seq(
                    tok(lg.IDENT, "param"),
                    many(seq(
                        tok(lg.COMMA),
                        tok(lg.IDENT, "param"),
                    ))
                ),
                tok(lg.RBRACKET),
            )),
            tok(lg.ARROW),
            g.rhs.set_id("rhs"),
            tok(lg.SEMICOLON)
        )
    @ast_transformer(grammar, "rule_def")
    def _transform_rule_def(ast):
        name = ast.get_child_by_id("name").value
        params = ast.get_children_by_id("param")
        if not params:
            new_ast = Ast("rule_def")
        else:
            new_ast = Ast("macro_def")
            params_ast = Ast("parameters")
            new_ast.add_child(params_ast)
            for param in params:
                params_ast.add_child(Ast("param", param.value))
        new_ast.set_attr("name", name)
        rhs = ast.get_children_by_id("rhs")[0]
        new_ast.add_child(rhs)
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
            seq(tok(lg.LPAREN), g.rhs, tok(lg.RPAREN)),
        )
    @ast_transformer(grammar, "element")
    def _transform_element(ast):
        children = ast.get_children()
        if len(children) == 1:
            return children[0]
        else:
            return children[1]

    @rule(grammar, "atom")
    def _atom(g):
        return seq(
            opt(seq(tok(lg.IDENT, "id"), tok(lg.HASH))),
            choice(
                tok(lg.TOKEN_TYPE, "token_type"),
                seq(
                    tok(lg.IDENT, "rule"),
                    opt(seq(
                        tok(lg.LBRACKET),
                        seq(
                            g.rhs.set_id("arg"),
                            many(seq(
                                tok(lg.COMMA),
                                g.rhs.set_id("arg"),
                            ))
                        ),
                        tok(lg.RBRACKET),
                    )),
                ),
                tok(lg.KEYWORD, "keyword"),
            )
        )
    @ast_transformer(grammar, "atom")
    def _transform_atom(ast):
        is_macro_call = False
        id_ast = ast.get_child_by_id("id")
        token_type_ast = ast.get_child_by_id("token_type")
        if token_type_ast:
            ret = Ast("token_type", token_type_ast.value)
        else:
            rule_ast = ast.get_child_by_id("rule")
            if rule_ast:
                args = ast.get_children_by_id("arg")
                is_macro_call = len(args) > 0
                if not is_macro_call:
                    ret = Ast("rule", rule_ast.value)
                else:
                    ret = Ast("macro_call", rule_ast.value)
                    for arg in args:
                        ret.add_child(arg)
            else:
                keyword_ast = ast.get_child_by_id("keyword")
                ret = Ast("keyword", keyword_ast.value[1:-1])
        ret.id = ""
        if id_ast:
            if not is_macro_call:
                ret.set_attr("identifier", id_ast.value)
            else:
                raise Exception("macro calls cannot be labeled")
        return ret

    @rule(grammar, "multiplier")
    def _multiplier(_):
        return choice(
            tok(lg.QUESTION_MARK),
            tok(lg.STAR),
            tok(lg.PLUS)
        )

    return grammar