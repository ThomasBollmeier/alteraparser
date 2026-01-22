from typing import Any


class Ast:
    def __init__(self, name: str, value=None, id_:str= ""):
        self.name = name
        self.value = value
        self.id = id_
        self.children: list[Ast] = []
        self.attributes: dict[str, Any] = {}

    def clone(self) -> 'Ast':
        cloned_ast = Ast(self.name, self.value, self.id)
        cloned_ast.attributes = self.attributes.copy()
        for child in self.children:
            cloned_ast.add_child(child.clone())
        return cloned_ast

    def add_child(self, child: 'Ast'):
        self.children.append(child)

    def get_children(self) -> list['Ast']:
        return self.children

    def get_nth_child(self, n: int) -> 'Ast':
        return self.children[n]

    def get_children_by_name(self, name: str) -> list['Ast']:
        return [child for child in self.children if child.name == name]

    def get_child_by_id(self, id_: str, clear_id: bool=True) -> 'Ast | None':
        for child in self.children:
            if child.id == id_:
                if clear_id:
                    cloned_child = child.clone()
                    cloned_child.id = ""
                    return cloned_child
                return child
        return None

    def get_children_by_id(self, id_: str, clear_id: bool=True) -> list['Ast']:
        if clear_id:
            ret = []
            for child in self.children:
                if child.id != id_:
                    continue
                cloned_child = child.clone()
                cloned_child.id = ""
                ret.append(cloned_child)
            return ret
        return [child for child in self.children if child.id == id_]

    def set_attr(self, name: str, value: Any=True):
        self.attributes[name] = value

    def get_attr(self, name: str) -> Any:
        return self.attributes.get(name)

    def has_attr(self, name: str) -> bool:
        return name in self.attributes

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
        id_str = f' id="{ast.id}"' if ast.id else ''
        if ast.value is None:
            if ast.children:
                self._write_line(f'<{ast.name}{id_str}>')
            else:
                self._write_line(f'<{ast.name}{id_str}/>')
        else:
            if ast.children:
                self._write_line(f'<{ast.name}{id_str}> {ast.value}')
            else:
                self._write_line(f'<{ast.name}{id_str}> {ast.value} </{ast.name}>')

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
