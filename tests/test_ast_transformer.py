from alteraparser.ast_ import Ast, AstTransformer, transform_ast


def test_transformer_preserves_id_for_replaced_node():
    transformer = AstTransformer()

    root = Ast("binary", id_="node-42")
    left = Ast("number", value="2", id_="left-1")
    right = Ast("number", value="3", id_="right-2")
    root.add_child(left)
    root.add_child(right)

    @transform_ast(transformer, "binary")
    def binary_transformer(ast: Ast) -> Ast:
        replacement = Ast("sum")
        replacement.add_child(ast.children[0])
        replacement.add_child(ast.children[1])
        return replacement

    transformed = transformer.transform(root)

    assert transformed.id == "node-42"
    assert transformed.name == "sum"
    assert [child.id for child in transformed.children] == ["left-1", "right-2"]


def test_transformer_preserves_id_without_replacement():
    transformer = AstTransformer()
    ast = Ast("literal", value="x", id_="leaf-7")

    transformed = transformer.transform(ast)

    assert transformed is ast
    assert transformed.id == "leaf-7"
