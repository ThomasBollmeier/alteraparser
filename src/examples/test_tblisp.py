from tblisp_parser import create_tblisp_parser

code = """
(valid? account)
(test (my-func a b) c)
; Das obligatoriche Beispiel;-)
(writeln ; <-- callee
    "Hallo Welt!" ; <-- first argument
    (language-code german))
"""

parser = create_tblisp_parser()  # .debug_mode()
ast = parser.parse_string(code)

print(ast.to_xml())

