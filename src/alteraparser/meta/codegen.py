from typing import List, Dict
from alteraparser.ast_ import Ast, walk, AstWalker


class CodeGenerator:

    def __init__(self, indent_size: int=4):
        self._indent_size = indent_size
        self._indent_level = 0
        self._lines = []
        self._line = ""
        self._keyword_map = {}
        self._rule_names = []

    def generate_code(self, language_name: str, ast: Ast) -> List[str]:

        self._generate_import_statements()

        self._generate_lexer_grammar(f"{language_name}LexerGrammar", ast)
        self._write_line()

        self._generate_grammar(language_name, self._keyword_map, ast)
        self._write_line()

        self._generate_parser(language_name, self._rule_names)

        if self._line:
            self._lines.append(self._line)
        return self._lines[:]

    def _generate_import_statements(self):
        self._write_line("from alteraparser.lexer_grammar import LexerGrammar")
        self._write_line("from alteraparser.grammar import *")
        self._write_line("from alteraparser.lexer import Lexer")
        self._write_line("from alteraparser.parser import Parser")
        self._write_line()

    def _generate_lexer_grammar(self, name: str, ast: Ast):
        kw_finder = KeywordFinder()
        walk(ast, kw_finder)
        self._keyword_map = kw_finder.get_keyword_map()

        tt_finder = TokenTypeFinder()
        walk(ast, tt_finder)
        token_types = tt_finder.get_token_types()

        self._write_line(f"class {name}(LexerGrammar):")
        self._indent()

        self._write_line("def __init__(self):")
        self._indent()

        self._write_line("LexerGrammar.__init__(self)")

        for keyword, token_type in self._keyword_map.items():
            self._write_line(f"self.add_rule(\"{token_type}\", r\"\\b{keyword}\\b\")")

        for token_type, pattern, ignore in token_types:
            if not ignore:
                self._write_line(f"self.add_rule(\"{token_type}\", r\"{pattern}\")")
            else:
                self._write_line(f"self.add_rule(\"{token_type}\", r\"{pattern}\", ignore=True)")

        self._dedent()
        self._dedent()

    def _generate_grammar(self, language_name: str, keyword_map_inv: Dict[str, str], ast: Ast):
        snake_name = self._camel_to_snake(language_name)
        self._write_line(f"def create_{snake_name}_grammar() -> Grammar:")
        self._indent()
        self._write_line("grammar = Grammar()")
        self._write_line(f"lg = {language_name}LexerGrammar()")
        self._write_line()

        grammar_printer = GrammarPrinter(self, keyword_map_inv)
        walk(ast, grammar_printer)

        self._write_line("return grammar")
        self._dedent()

        self._rule_names = grammar_printer.get_rule_names()

    def _generate_parser(self, language_name: str, rule_names: List[str]):
        self._write_line(f"class {language_name}Parser:")
        self._indent()
        self._write_line("def __init__(self):")
        self._indent()
        self._write_line(f"self._lexer_grammar = {language_name}LexerGrammar()")
        self._write_line(f"grammar = create_{self._camel_to_snake(language_name)}_grammar()")
        self._write_line(f"self._parser = Parser(grammar)")
        self._dedent()
        self._write_line()
        for rule_name in rule_names:
            self._write_line(f"def parse_{rule_name}(self, text: str) -> Ast | None:")
            self._indent()
            self._write_line("lexer = Lexer(self._lexer_grammar, text)")
            self._write_line(f"return self._parser.parse(lexer, rule_name=\"{rule_name}\")")
            self._dedent()
            self._write_line()
        self._dedent()

    @staticmethod
    def _camel_to_snake(name: str) -> str:
        snake = ""
        for i, c in enumerate(name):
            if c.isupper() and i > 0:
                snake += "_"
            snake += c.lower()
        return snake

    def _indent(self):
        self._indent_level += 1

    def _dedent(self):
        self._indent_level -= 1

    def _write(self, text: str=""):
        if not self._line:
            self._line = self._indent_level * self._indent_size * " "
        self._line += text

    def _write_line(self, text: str=""):
        self._write(text)
        self._lines.append(self._line)
        self._line = ""


class KeywordFinder(AstWalker):

    def __init__(self):
        AstWalker.__init__(self)
        self._num_keywords = 0
        self._keyword_map = {}

    def get_keyword_map(self) -> Dict[str, str]:
        return self._keyword_map

    def on_enter(self, ast: Ast):
        if ast.name != "keyword":
            return
        keyword = ast.value
        if keyword not in self._keyword_map:
            self._num_keywords += 1
            self._keyword_map[keyword] = f"$KEYWORD_{self._num_keywords}"


class TokenTypeFinder(AstWalker):

    def __init__(self):
        AstWalker.__init__(self)
        self._token_types = []

    def get_token_types(self):
        return self._token_types

    def on_enter(self, ast: Ast):
        if ast.name != "token_type_def":
            return
        token_type = ast.get_attr("name")
        pattern = ast.get_attr("regex")
        ignore = ast.has_attr("ignore")
        self._token_types.append((token_type, pattern, ignore))

class GrammarPrinter(AstWalker):

    def __init__(self, generator: CodeGenerator, keyword_map: Dict[str, str]):
        AstWalker.__init__(self)
        self._generator = generator
        self._keyword_map = keyword_map
        self._in_macro_def = False
        self._call_args = []
        self._rule_names = []

    def get_rule_names(self):
        return self._rule_names

    def on_enter(self, ast: Ast):
        if self._in_macro_def: # ignore macro definitions
            return

        if ast.has_attr("multiplier"):
            multiplier = ast.get_attr("multiplier")
            match multiplier:
                case "?":
                    self._write("opt(")
                case "*":
                    self._write("many(")
                case "+":
                    self._write("one_or_more(")
            if len(ast.children) > 1:
                self._write_line("seq(")
            else:
                self._write_line("")
            self._open_call(len(ast.children))
            self._indent()
            return

        identifier = ast.get_attr("identifier") if ast.has_attr("identifier") else None

        match ast.name:
            case "rule_def":
                name = ast.get_attr("name")
                self._write_line(f"@rule(grammar, \"{name}\")")
                self._write_line(f"def _{name}(g: Grammar):")
                self._indent()
                self._write("return ")
                self._rule_names.append(name)
            case "macro_def":
                self._in_macro_def = True
            case "branches":
                if len(ast.children) > 1:
                    self._write_line("choice(")
                    self._open_call(len(ast.children))
                    self._indent()
            case "sequence":
                self._write_line("seq(")
                self._open_call(len(ast.children))
                self._indent()
            case "rule":
                rule_name = ast.value
                if not identifier:
                    self._write_line(f"g.{rule_name}{self._delim()}")
                else:
                    self._write_line(f"g.{rule_name}.set_id(\"{identifier}\"){self._delim()}")
            case "keyword":
                keyword = ast.value
                token_type = self._keyword_map[keyword]
                if not identifier:
                    self._write_line(f"tok(lg.{token_type}){self._delim()} # <-- '{keyword}'")
                else:
                    self._write_line(f"tok(lg.{token_type}, \"{identifier}\"){self._delim()} # <-- '{keyword}'")
            case "token_type":
                token_type = ast.value
                if not identifier:
                    self._write_line(f"tok(lg.{token_type}){self._delim()}")
                else:
                    self._write_line(f"tok(lg.{token_type}, \"{identifier}\"){self._delim()}")

    def on_exit(self, ast: Ast):
        if self._in_macro_def:
            if ast.name == "macro_def":
                self._in_macro_def = False
            return

        if ast.has_attr("multiplier"):
            self._dedent()
            self._close_call()
            if len(ast.children) > 1:
                self._write_line(f")){self._delim()}")
            else:
                self._write_line(f"){self._delim()}")
            return

        match ast.name:
            case "rule_def":
                self._dedent()
                self._write_line()
            case "branches":
                if len(ast.children) > 1:
                    self._dedent()
                    self._close_call()
                    self._write_line(f"){self._delim()}")
            case "sequence":
                self._dedent()
                self._close_call()
                self._write_line(f"){self._delim()}")

    def _open_call(self, num_args: int):
        self._call_args.append((0, num_args))

    def _close_call(self):
        self._call_args.pop()

    def _delim(self):
        if not self._call_args:
            return ""
        arg_idx, num_args = self._call_args[-1]
        if arg_idx < num_args - 1:
            self._call_args[-1] = (arg_idx + 1, num_args)
            return ","
        else:
            return ""

    def _indent(self):
        self._generator._indent()

    def _dedent(self):
        self._generator._dedent()

    def _write(self,  text: str=""):
        self._generator._write(text)

    def _write_line(self, text: str=""):
        self._generator._write_line(text)
