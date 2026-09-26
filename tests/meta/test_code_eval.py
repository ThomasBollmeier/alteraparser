import types
import sys
from typing import List
from alteraparser.meta.parser import Parser
from alteraparser.meta.codegen import CodeGenerator
from alteraparser.ast_ import AstStrWriter

def test_codegen():

    source = """
        tokens {
            WSPACE regex(\s+) ignore;
            NUMBER regex(\d+);
            PLUS regex([+]);
            MINUS regex(\-);
            STAR regex([*]);
            SLASH regex(/);
            LPAREN regex([(]);
            RPAREN regex([)]);
        }
        
        expr -> term ((op#PLUS | op#MINUS) term)*;
        term -> factor ((op#STAR | op#SLASH) factor)*;
        factor -> NUMBER | LPAREN expr RPAREN;

    """

    parser = Parser()
    ast = parser.parse(source)
    assert ast is not None

    lines = CodeGenerator().generate_code("Expr", ast)

    mod = create_parser_module("expr_mod", lines)
    sys.modules["expr_mod"] = mod

    from expr_mod import ExprParser

    expr_parser = ExprParser()
    print(expr_parser)

    expr_code = "2 + 5 * (4 + 4)"
    expr_ast = expr_parser.parse_expr(expr_code)
    assert expr_ast is not None

    writer = AstStrWriter()
    ast_str = writer.write_ast_to_str(expr_ast)
    print(ast_str)

def create_parser_module(module_name: str, lines: List[str]) -> types.ModuleType:
    generated_code = "\n".join(lines)
    module = types.ModuleType(module_name)
    exec(generated_code, module.__dict__)
    return module