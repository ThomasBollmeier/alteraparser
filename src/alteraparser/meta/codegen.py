from typing import List, Dict
from alteraparser.ast_ import Ast, walk, AstWalker


class CodeGenerator:

    def __init__(self, indent_size: int=4):
        self._indent_size = indent_size
        self._indent_level = 0
        self._lines = []
        self._line = ""

    def generate_lexer_grammar(self, name: str, ast: Ast) -> List[str]:
        kw_finder = KeywordFinder()
        walk(ast, kw_finder)
        keyword_map = kw_finder.get_keyword_map()

        tt_finder = TokenTypeFinder()
        walk(ast, tt_finder)
        token_types = tt_finder.get_token_types()

        self._write_line("from alteraparser.lexer_grammar import LexerGrammar")
        self._write_line()

        self._write_line(f"class {name}(LexerGrammar):")
        self._indent()

        self._write_line("def __init__(self):")
        self._indent()

        self._write_line("LexerGrammar.__init__(self)")

        for keyword, token_type in keyword_map.items():
            self._write_line(f"self.add_rule(\"{token_type}\", r\"\\b{keyword}\\b\")")

        for token_type, pattern, ignore in token_types:
            if not ignore:
                self._write_line(f"self.add_rule(\"{token_type}\", r\"{pattern}\")")
            else:
                self._write_line(f"self.add_rule(\"{token_type}\", r\"{pattern}\", ignore=True)")

        self._dedent()
        self._dedent()

        if self._line:
            self._lines.append(self._line)

        return self._lines[:]

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