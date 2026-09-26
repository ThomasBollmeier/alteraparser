import types
import sys
from alteraparser.meta.codegen import generate_python_module_code
from alteraparser.ast_ import AstTransformer, AstStrWriter, Ast

def test_code_evaluation():

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
        
        expr -> term ((PLUS | MINUS) term)*;
        term -> factor ((STAR | SLASH) factor)*;
        factor -> NUMBER | LPAREN expr RPAREN;

    """

    code = generate_python_module_code(source, "Expr")

    mod = create_parser_module("expr_mod", code)
    sys.modules["expr_mod"] = mod

    from expr_mod import ExprParser

    expr_parser = ExprParser()
    print(expr_parser)

    expr_code = "2 + 5 * (7 - 3 + 4)"
    ast = expr_parser.parse_expr(expr_code)
    assert ast is not None

    ast = parse_tree_to_ast(ast)

    writer = AstStrWriter()
    ast_str = writer.write_ast_to_str(ast)
    print(ast_str)

def create_parser_module(module_name: str, code: str) -> types.ModuleType:
    module = types.ModuleType(module_name)
    exec(code, module.__dict__)
    return module

def parse_tree_to_ast(ast):
    transformer = AstTransformer()

    def factor_transformer(ast: Ast) -> Ast:
        match len(ast.children):
            case 1:
                return ast.children[0]
            case 3:
                return ast.children[1]
            case _:
                raise Exception("Invalid factor node")

    def binary_op_transformer(ast: Ast) -> Ast:
        if len(ast.children) == 1:
            return ast.children[0]
        else:
            left = ast.children[0]
            for i in range(1, len(ast.children), 2):
                op = ast.children[i]
                right = ast.children[i + 1]
                match op.value:
                    case "+":
                        name = "add"
                    case "-":
                        name = "sub"
                    case "*":
                        name = "mul"
                    case "/":
                        name = "div"
                    case _:
                        raise Exception(f"Unknown operator: {op.value}")
                new_node = Ast(name=name)
                new_node.add_child(left)
                new_node.add_child(right)
                left = new_node
            return left

    transformer.register_transformer("expr", binary_op_transformer)
    transformer.register_transformer("term", binary_op_transformer)
    transformer.register_transformer("factor", factor_transformer)

    return transformer.transform(ast)