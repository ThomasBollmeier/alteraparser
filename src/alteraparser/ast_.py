class Ast:
    def __init__(self, name: str, value=None):
        self.name = name
        self.value = value
        self.children: list[Ast] = []

    def add_child(self, child: 'Ast'):
        self.children.append(child)

    def get_children(self) -> list['Ast']:
        return self.children

    def get_nth_child(self, n: int) -> 'Ast':
        return self.children[n]

    def get_children_by_name(self, name: str) -> list['Ast']:
        return [child for child in self.children if child.name == name]

    def __getitem__(self, item):
        return self.children[item]


class AstStrWriter:
    def __init__(self, indent_size: int = 2):
        self._indent_level = 0
        self._indent_size = indent_size
        self._output = ""

    def write_ast_to_str(self, ast: Ast) -> str:
        self._output = ""
        self._indent_level = 0
        self._write_ast(ast)
        return self._output

    def _write_ast(self, ast: Ast):
        if ast.value is None:
            if ast.children:
                self._write_line(f'<{ast.name}>')
            else:
                self._write_line(f'<{ast.name}/>')
        else:
            if ast.children:
                self._write_line(f'<{ast.name}> {ast.value}')
            else:
                self._write_line(f'<{ast.name}> {ast.value} </{ast.name}>')

        self._indent_level += 1

        for child in ast.children:
            self._write_ast(child)

        self._indent_level -= 1

        if ast.children:
            self._write_line(f'</{ast.name}>')

    def _write(self, text: str):
        for _ in range(self._indent_level * self._indent_size):
            self._output += ' '
        self._output += text

    def _write_line(self, text: str):
        self._write(text)
        self._output += '\n'
