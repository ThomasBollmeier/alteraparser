from alteraparser.meta.parser import Parser
from alteraparser.meta.codegen import CodeGenerator

def test_codegen():

    source = """
        tokens {
            WSPACE regex(\s+) ignore;
            IDENTIFIER regex([a-zA-Z_][a-zA-Z0-9_]*);
            LBRACE regex([{]);    
            RBRACE regex([}]);
            LPAREN regex([(]);
            RPAREN regex([)]);
        }

        -- Class Declaration
        class_decl -> 'class' name#IDENTIFIER block< 
            attrs_decl
            methods_decl
            >;
        attrs_decl -> 'attrs' block< 
            ('attr' attr#IDENTIFIER)+
        >;
        methods_decl -> 'methods' block<
            ('method' method#IDENTIFIER LPAREN RPAREN)+
        >; 

        block<body> -> LBRACE body RBRACE | 'begin' body 'end';
    """

    parser = Parser()
    ast = parser.parse(source)

    assert ast is not None

    lines = CodeGenerator().generate_code("MyLang", ast)
    for line in lines:
        print(line)
