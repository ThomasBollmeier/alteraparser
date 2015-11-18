from alteraparser import *
from alteraparser.ast import AST

# Define BNF-like grammar


def esc_trnsf(ast):
    return AST('esc', text="'")


def terminal_trnsf(ast):
    return AST('term', text=ast.text[1:-1])


quote = single_char("'")
non_quote = quote.clone().negate()
question_mark = single_char('?')
plus = single_char('+')
star = single_char('*')
cardinality = fork(question_mark, plus, star)
par_open = single_char('(')
par_close = single_char(')')
pipe = token(single_char('|'), 'pipe')
assign = single_char('=')
dot = single_char('.')
semicolon = token(single_char(';'), 'semicolon')
alpha = char_range('a', 'z')
num = char_range('0', '9')
alpha_num = fork(alpha, num)
underscore = single_char('_')
whitespace = token(characters(' ', '\t', '\n'), 'ws').set_ignore()
newline = keyword('<newline>', name='newline')
tab = keyword('<tab>', name='tab')
space = keyword('<space>', name='space')
special_char = fork(newline, tab, space)

esc = fork([single_char('\\'), quote])\
    .set_name('esc')\
    .transform_ast(esc_trnsf)

terminal = fork([quote,
                 many(fork(esc, non_quote)),
                 quote]).set_name('term')\
    .transform_ast(terminal_trnsf)

rule_name = fork([alpha,
                  many(fork(alpha_num,
                            fork([underscore, alpha_num])))])\
    .set_name('rule_name').set_unique()


@group(is_unique=True)
def prod_rule_stmt(self, start, end):
    global rule_name, assign, semicolon
    start > many(whitespace) > \
        rule_name.clone() > \
        many(whitespace) > \
        assign.clone() > \
        many(whitespace) > \
        expr_stmt() > \
        many(whitespace) > \
        semicolon.clone() > \
        end


@group()
def expr_stmt(self, start, end):
    global pipe, whitespace
    start > branch_stmt() > \
        many(fork([
            one_to_many(whitespace),
            pipe,
            one_to_many(whitespace),
            branch_stmt()])) > end


@group()
def branch_stmt(self, start, end):
    global terminal, rule_name, special_char, cardinality
    v = start.clone()
    start > terminal.clone() > v
    start > rule_name.clone() > v
    start > range_stmt() > v
    start > special_char.clone() > v
    start > comp_stmt() > v
    v > one_to_many(whitespace) > start
    v > optional(cardinality) > end


@group(is_unique=True)
def comp_stmt(self, start, end):
    global par_open, par_close, whitespace
    start > par_open.clone() > \
        optional(whitespace) > \
        expr_stmt() > \
        optional(whitespace) > \
        par_close.clone() > \
        end


@group(is_unique=True)
def range_stmt(self, start, end):
    global dot, terminal
    from_ = terminal.set_id('from')
    to =  terminal.set_id('to')
    start > from_ > dot.clone() > dot.clone() > to > end


bnf_grammar = grammar('bnf', one_to_many(fork(
    [many(whitespace),
     prod_rule_stmt(),
     many(whitespace)])))

