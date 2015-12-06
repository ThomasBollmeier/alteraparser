from alteraparser import *
from alteraparser.ast import AST
from alteraparser.parser import Parser


def create_tblisp_parser():
    return Parser(tblisp())


def _whitespace_trnsf(ast):
    #--beginedit whitespace
    return ast
    #--endedit


@group(name='whitespace', is_unique=False, transform_ast_fn=_whitespace_trnsf)
def _whitespace(self, start, end):
    start > _branch_1() > end
    start > _branch_2() > end
    start > _branch_3() > end


def _alpha_trnsf(ast):
    #--beginedit alpha
    return ast
    #--endedit


@group(name='alpha', is_unique=False, transform_ast_fn=_alpha_trnsf)
def _alpha(self, start, end):
    start > _branch_4() > end
    start > _branch_5() > end


def _digit_trnsf(ast):
    #--beginedit digit
    return ast
    #--endedit


@group(name='digit', is_unique=False, transform_ast_fn=_digit_trnsf)
def _digit(self, start, end):
    curr = start
    curr = curr > char_range('0', '9')
    curr > end


def _alpha_num_trnsf(ast):
    #--beginedit alpha_num
    return ast
    #--endedit


@group(name='alpha_num', is_unique=False, transform_ast_fn=_alpha_num_trnsf)
def _alpha_num(self, start, end):
    start > _branch_6() > end
    start > _branch_7() > end


def _var_name_trnsf(ast):
    #--beginedit var_name
    return AST('varname', text=ast.text)
    #--endedit


@group(name='var_name', is_unique=False, transform_ast_fn=_var_name_trnsf)
def _var_name(self, start, end):
    curr = start
    curr = curr > _alpha()
    curr = curr > many(_comp_1())
    curr = curr > optional(characters('?'))
    curr > end


def _expr_trnsf(ast):
    #--beginedit expr
    return ast.ast_children[0].ast_children[0]
    #--endedit


@group(name='expr', is_unique=False, transform_ast_fn=_expr_trnsf)
def _expr(self, start, end):
    start > _branch_10() > end
    start > _branch_11() > end


def _call_trnsf(ast):
    #--beginedit call
    res = AST('call')
    node = AST('callee')
    res.add_child(node)
    callee = ast['#callee'][0]
    callee.id = ''
    node.add_child(callee)
    args = ast['#arg']
    if args:
        node = AST('arguments')
        res.add_child(node)
        for arg in args:
            arg.id = ''
            node.add_child(arg)
    return res
    #--endedit


@group(name='call', is_unique=False, transform_ast_fn=_call_trnsf)
def _call(self, start, end):
    curr = start
    curr = curr > keyword('(')
    curr = curr > many(_whitespace())
    curr = curr > _expr().set_id('callee')
    curr = curr > one_to_many(_whitespace())
    curr = curr > optional(fork([_expr().set_id('arg'), many(fork([one_to_many(_whitespace()), _expr().set_id('arg')]))]))
    curr = curr > many(_whitespace())
    curr = curr > keyword(')')
    curr > end


def _tblisp_trnsf(ast):
    #--beginedit tblisp
    res = AST('tblisp')
    content = ast['#content']
    for item in content:
        item.id = ''
        res.add_child(item)
    return res
    #--endedit


@group(name='tblisp', is_unique=False, transform_ast_fn=_tblisp_trnsf)
def tblisp(self, start, end):
    curr = start
    curr = curr > optional(_whitespace())
    curr = curr > one_to_many(_whitespace())
    curr = curr > fork([_call().set_id('content'), many(fork([one_to_many(_whitespace()), _call().set_id('content')]))])
    curr = curr > one_to_many(_whitespace())
    curr = curr > optional(_whitespace())
    curr > end


@group()
def _branch_1(self, start, end):
        curr = start
        curr = curr > single_char(' ')
        curr > end


@group()
def _branch_10(self, start, end):
        curr = start
        curr = curr > _var_name()
        curr > end


@group()
def _branch_11(self, start, end):
        curr = start
        curr = curr > _call()
        curr > end


@group()
def _branch_2(self, start, end):
        curr = start
        curr = curr > single_char('\t')
        curr > end


@group()
def _branch_3(self, start, end):
        curr = start
        curr = curr > single_char('\n')
        curr > end


@group()
def _branch_4(self, start, end):
        curr = start
        curr = curr > char_range('a', 'z')
        curr > end


@group()
def _branch_5(self, start, end):
        curr = start
        curr = curr > char_range('A', 'Z')
        curr > end


@group()
def _branch_6(self, start, end):
        curr = start
        curr = curr > _alpha()
        curr > end


@group()
def _branch_7(self, start, end):
        curr = start
        curr = curr > _digit()
        curr > end


@group()
def _branch_8(self, start, end):
        curr = start
        curr = curr > _alpha_num()
        curr > end


@group()
def _branch_9(self, start, end):
        curr = start
        curr = curr > keyword('-')
        curr = curr > _alpha_num()
        curr > end


@group()
def _branches_1(self, start, end):
        start > _branch_8() > end
        start > _branch_9() > end


@group()
def _comp_1(self, start, end):
        start > _branches_1() > end


