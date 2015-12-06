from tblisp_parser import create_tblisp_parser

code = """
(valid? account)
(test (my-func a b) c)
"""

parser = create_tblisp_parser()
ast = parser.parse_string(code)

print(ast.to_xml())
