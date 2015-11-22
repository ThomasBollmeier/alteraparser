from alteraparser import *
from alteraparser.ast import AST

# Define BNF-like grammar


quote = single_char("'")
non_quote = quote.clone().negate()
question_mark = single_char('?')
plus = single_char('+')
star = single_char('*')
tilde = single_char('~')
ampersand = token(single_char('&'), 'ampersand')\
    .transform_ast(lambda ast: AST('no-ws'))
opt_ws = keyword('&?').transform_ast(lambda ast: AST('optional-ws'))
par_open = single_char('(')
par_close = single_char(')')
pipe = token(single_char('|'), 'pipe')
assign = single_char('=')
dot = single_char('.')
semicolon = token(single_char(';'), 'semicolon')
hash_char = single_char('#')
alpha = char_range('a', 'z')
num = char_range('0', '9')
alpha_num = fork(alpha, num)
underscore = single_char('_')
whitespace = token(characters(' ', '\t', '\n'), 'ws').set_ignore()
newline = keyword('<newline>', name='newline')
tab = keyword('<tab>', name='tab')
space = keyword('<space>', name='space')
ws = keyword('WHITESPACE', name='WHITESPACE')


def cardinality_trnsf(ast):
    children = ast.children
    if len(children) == 1:
        no_whitespace = None
        value = children[0].text
    else:
        opt_no_ws = children[0]
        if opt_no_ws.ast_children:
            no_whitespace = opt_no_ws.ast_children[0]
        else:
            no_whitespace = None
        value = children[1].text
    res = AST('cardinality')
    res.add_child(AST('value', text=value))
    if no_whitespace:
        res.add_child(no_whitespace)
    return res


cardinality = fork(
    question_mark,
    [optional(ampersand), plus],
    [optional(ampersand), star])\
    .set_name('cardinality')\
    .transform_ast(cardinality_trnsf)


def special_char_trnsf(ast):
    name = ast.children[0].name
    return AST(name)


special_char = fork(newline, tab, space).transform_ast(special_char_trnsf)


def esc_trnsf(ast):
    return AST('esc', text="'")


esc = fork([single_char('\\'), quote])\
    .set_name('esc')\
    .transform_ast(esc_trnsf)


def terminal_trnsf(ast):
    return AST('term', text=ast.text[1:-1])


terminal = fork([quote,
                 many(fork(esc, non_quote)),
                 quote]).set_name('term')\
    .transform_ast(terminal_trnsf)


def rule_name_trnsf(ast):
    return AST('rule-name', text=ast.text)


rule_name = fork([alpha,
                  many(fork(alpha_num,
                            fork([underscore, alpha_num])))])\
    .set_name('rule_name')\
    .set_unique()\
    .transform_ast(rule_name_trnsf)


def id_trnsf(ast):
    return AST('id', text=ast.text)


id_name = fork([alpha,
                many(fork(alpha_num,
                          fork([underscore, alpha_num])))])\
    .set_name('id_name')\
    .set_unique()\
    .transform_ast(id_trnsf)


def rule_trnsf(ast):
    res = AST('rule')
    r_name = ast['rule-name']
    if r_name:
        r_name = r_name[0].text
    else:
        r_name = ast['WHITESPACE'][0].text
    res.add_child(AST('name', text=r_name))
    rhs = ast['#rhs'][0]
    rhs.id = ''
    res.add_child(rhs)
    return res


@group(name='rule', is_unique=True, transform_ast_fn=rule_trnsf)
def prod_rule_stmt(self, start, end):
    global whitespace, rule_name, ws, assign, semicolon
    start > many(whitespace) > \
        fork(rule_name, ws) > \
        many(whitespace) > \
        assign.clone() > \
        many(whitespace) > \
        expr_stmt().set_id('rhs') > \
        many(whitespace) > \
        semicolon.clone() > \
        end


def expr_transf(ast):
    branches = ast['#branch']
    if len(branches) == 1:
        res = branches[0]
    else:
        res = AST('branches')
        for branch in branches:
            branch.id = ''
            res.add_child(branch)
    return res


@group(transform_ast_fn=expr_transf)
def expr_stmt(self, start, end):
    global pipe, whitespace
    start > branch_stmt().set_id('branch') > \
        many(fork([
            one_to_many(whitespace),
            pipe,
            one_to_many(whitespace),
            branch_stmt().set_id('branch')])) > end


def branch_trnsf(ast):
    res = AST('branch')
    for content in ast['#content']:
        if content.ast_children:
            node_fork, opt_id, opt_cardinal = content.ast_children
            node = node_fork.ast_children[0]
            if opt_id.ast_children:
                id_node = opt_id.ast_children[0].ast_children[0]
                node.add_child(AST('id', text=id_node.text))
            if opt_cardinal.ast_children:
                cardinal = opt_cardinal.ast_children[0]
                node.add_child(cardinal)
        else:
            node = content
            node.id = ''
        res.add_child(node)
    return res


@group('branch', transform_ast_fn=branch_trnsf)
def branch_stmt(self, start, end):
    global terminal, rule_name, whitespace,\
        special_char, cardinality, ampersand, hash_char, opt_ws
    v = start.clone()
    start > fork([fork(
        terminal.clone(),
        rule_name.clone(),
        range_stmt(),
        special_char.clone(),
        comp_stmt()),
        optional(fork([hash_char, id_name])),
        optional(cardinality)]).set_id('content') >\
        v
    v > one_to_many(whitespace) >\
        optional(fork([ampersand.set_id('content'),
                       one_to_many(whitespace)])) > start
    v > one_to_many(whitespace) >\
        optional(fork([opt_ws.set_id('content'),
                       one_to_many(whitespace)])) > start
    v.connect(end)


def comp_trnsf(ast):
    res = AST('comp')
    expr = ast['#expr'][0]
    expr.id = ''
    res.add_child(expr)
    return res


@group('comp', is_unique=True, transform_ast_fn=comp_trnsf)
def comp_stmt(self, start, end):
    global par_open, par_close, whitespace
    start > par_open.clone() > \
        optional(whitespace) > \
        expr_stmt().set_id('expr') > \
        optional(whitespace) > \
        par_close.clone() > \
        end


def range_trnsf(ast):
    res = AST('range')
    from_ = ast['#from'][0]
    to = ast['#to'][0]
    res.add_child(AST('from', text=from_.text))
    res.add_child(AST('to', text=to.text))
    return res


@group(name='range', is_unique=True, transform_ast_fn=range_trnsf)
def range_stmt(self, start, end):
    global dot, terminal
    from_ = terminal.set_id('from')
    to = terminal.set_id('to')
    start > from_ > dot.clone() > dot.clone() > to > end


def bnf_grammar_trnsf(ast):
    res = AST('bnf-grammar')
    for child in ast['#grammar-element']:
        child.id = ''
        res.add_child(child)
    return res

bnf_grammar = grammar('bnf',
                      [one_to_many(
                          fork([many(whitespace),
                                prod_rule_stmt().set_id('grammar-element'),
                                many(whitespace)]))],
                      bnf_grammar_trnsf)

