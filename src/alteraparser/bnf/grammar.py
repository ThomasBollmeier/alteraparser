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
par_open = single_char('(')
par_close = single_char(')')
pipe = token(single_char('|'), 'pipe')
assign = single_char('=')
semicolon = token(single_char(';'), 'semicolon')
alpha = char_range('a', 'z')
num = char_range('0', '9')
alpha_num = fork(alpha, num)
underscore = single_char('_')
whitespace = token(characters(' ', '\t', '\n'), 'ws').set_ignore()

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
    .set_name('rule_name')

cardinality = fork(question_mark, plus, star)


@group
def prod_rule_stmt(self, start, end):
    global rule_name, assign, semicolon
    start > rule_name.clone() > \
        optional(whitespace) > \
        assign.clone() > \
        optional(whitespace) > \
        expr_stmt() > \
        optional(whitespace) > \
        semicolon.clone() > \
        end


@group
def expr_stmt(self, start, end):
    global pipe, whitespace
    start > branch_stmt() > \
        many(fork([whitespace, pipe, whitespace, branch_stmt()])) > end


@group
def branch_stmt(self, start, end):
    global terminal, rule_name, cardinality
    v = start.clone()
    start > terminal.clone() > v
    start > rule_name.clone() > v
    start > comp_stmt() > v
    v > optional(cardinality) > end


@group
def comp_stmt(self, start, end):
    global par_open, par_close, whitespace
    start > par_open.clone() > \
        optional(whitespace) > \
        expr_stmt() > \
        optional(whitespace) > \
        par_close.clone() > \
        end


bnf_grammar = grammar('bnf', one_to_many(prod_rule_stmt()))
