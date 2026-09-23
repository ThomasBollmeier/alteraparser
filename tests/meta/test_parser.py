from alteraparser.meta.parser import Parser as MetaParser
from alteraparser.ast_ import AstStrWriter


def test_parser():
    parser = MetaParser()

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

    ast = parser.parse_text(source)

    assert ast is not None

    writer = AstStrWriter(indent_size=4)
    print(writer.write_ast_to_str(ast))