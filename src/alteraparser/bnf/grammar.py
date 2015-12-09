from alteraparser import *
from alteraparser.ast import AST

# Define BNF-like grammar


quote = single_char("'")
non_quote = quote.clone().negate()
question_mark = single_char('?')
plus = single_char('+')
star = single_char('*')
caret = single_char('^')
ampersand = token(single_char('&'), 'ampersand')\
    .transform_ast(lambda ast: AST('no-ws'))
opt_ws = keyword('&?').transform_ast(lambda ast: AST('optional-ws'))
par_open = single_char('(')
par_close = single_char(')')
bracket_open = single_char('[')
bracket_close = single_char(']')
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


def ws_trnsf(ast):
    res = AST('WHITESPACE')
    for child in ast.ast_children:
        res.add_child(child)
    return res

ws = ws.transform_ast(ws_trnsf)


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
    element = {
        '?': 'zero-to-one',
        '+': 'one-to-many',
        '*': 'many'
    }[value]
    res.add_child(AST(element))
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


def prod_rule_trnsf(ast):
    is_grammar = False
    is_unique = False
    annotations = ast['annotations']
    if annotations:
        if annotations[0]['grammar']:
            is_grammar = True
        if annotations[0]['unique']:
            is_unique = True
    if not is_grammar:
        res = AST('rule')
    else:
        res = AST('grammar')
    r_name = ast['rule-name']
    if r_name:
        r_name = r_name[0].text
    else:
        r_name = 'WHITESPACE'
    res.add_child(AST('name', text=r_name))
    rhs = ast['#rhs'][0]
    rhs.id = ''
    res.add_child(rhs)
    res.add_child(AST('unique', text=str(is_unique).lower()))
    return res


@group(name='rule', is_unique=True, transform_ast_fn=prod_rule_trnsf)
def prod_rule_stmt(self, start, end):
    global whitespace, rule_name, ws, assign, semicolon
    start > many(whitespace) > \
        many(annotation_stmt().set_id('annot')) > \
        fork(rule_name, ws) > \
        many(whitespace) > \
        assign.clone() > \
        many(whitespace) > \
        expr_stmt().set_id('rhs') > \
        many(whitespace) > \
        semicolon.clone() > \
        end


def annotation_trnsf(ast):
    res = AST('annotations')
    for node in ast['#annot']:
        name = node.name
        if name == 'grammar':
            res.add_child(AST('grammar'))
        elif name == 'unique':
            res.add_child(AST('unique'))
    return res


@group(name='annotation', is_unique=True, transform_ast_fn=annotation_trnsf)
def annotation_stmt(self, start, end):
    wspace = characters(' ', '\t')
    nl = single_char('\n')
    v = start.clone()
    annotations = fork(keyword('@grammar', name='grammar').set_id('annot'),
                       keyword('@unique', name='unique').set_id('annot'))
    start > many(fork(wspace, nl)) > annotations > \
        many(wspace) > nl.clone() > many(wspace) > v
    v > start
    v > end


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
    global ws, terminal, rule_name, whitespace,\
        special_char, cardinality, ampersand, hash_char, opt_ws
    v = start.clone()
    start > fork([fork(
        ws,
        terminal,
        rule_name,
        range_stmt(),
        charset_stmt(),
        special_char,
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


def charset_trnsf(ast):
    res = AST('charset')
    fork_node = ast.children[0]
    opt_neg = fork_node['#neg']
    if opt_neg[0].text:
        res.add_child(AST('negate'))
    char_elements = fork_node['#char-element']
    for char_elem in char_elements:
        char_elem.id = ''
        if char_elem.text:
            res.add_child(AST('char', text=char_elem.text))
        else:  # special character
            special_node = char_elem.ast_children[0]
            special_node.id = ''
            res.add_child(special_node)
    return res


@group(name='charset', is_unique=True, transform_ast_fn=charset_trnsf)
def charset_stmt(self, start, end):
    global bracket_open, bracket_close, \
        caret, special_char
    no_bracket_close = bracket_close.clone().negate()
    start > fork([
        bracket_open,
        optional(caret).set_id('neg'),
        one_to_many(fork(
            special_char.set_id('special'),
            no_bracket_close,
        ).set_id('char-element')),
        bracket_close
    ]) > end


def comment_trnsf(ast):
    return AST('comment', text=ast.text[2:-1])


@group(name='comment', is_unique=True, transform_ast_fn=comment_trnsf)
def comment_stmt(self, start, end):
    not_nl = single_char('\n').negate()
    start > keyword('--') > many(not_nl) > single_char('\n') > end


def bnf_grammar_trnsf(ast):
    res = AST('bnf-grammar')
    for child in ast['#grammar-element']:
        child.id = ''
        res.add_child(child)
    return res

bnf_grammar = grammar('bnf',
                      [one_to_many(
                          fork([many(whitespace),
                                fork(prod_rule_stmt().set_id('grammar-element'),
                                     comment_stmt().set_id('grammar-element')),
                                many(whitespace)]))],
                      bnf_grammar_trnsf)

