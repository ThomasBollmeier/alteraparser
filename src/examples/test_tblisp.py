from tblisp_parser import create_tblisp_parser

code = """
(valid? account)
(test (my-func a b) c)
(writeln "Hallo Welt!")
"""

code2 = "; Nur ein Kommentar...\n"

parser = create_tblisp_parser()
ast = parser.parse_string(code)

print(ast.to_xml())
