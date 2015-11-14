from alteraparser.ast import AST, TextNode
from alteraparser.io.string_input import StringInput
from alteraparser.syntaxgraph.match_finder import MatchFinder


class Parser(object):

    def __init__(self, grammar):
        self.__grammar = grammar

    def parse_string(self, code_str):
        finder = MatchFinder(StringInput(code_str))
        self.__grammar.get_dock_vertex().walk(finder)
        return self.__create_ast(finder.path)

    def parse_file(self, filepath):
        f = open(filepath, "r")
        code_lines = f.readlines()
        f.close()
        code = ''.join(code_lines)
        return self.parse_string(code)

    @staticmethod
    def __create_ast(path):
        root = None
        current = None
        stack = []
        text = ''
        for vertex, ch in path:
            if vertex.is_group_start():
                node = AST(vertex.name, vertex.id)
                if root is None:
                    root = node
                stack.append(node)
            elif vertex.is_group_end():
                node = stack.pop()
                node.add_child(TextNode(text))
                text = ''
                if stack:
                    parent = stack[-1]
                    if not vertex.ignore:
                        transformed_node = vertex.transform_ast_fn(node)
                        parent.add_child(transformed_node)
            if ch is not None:
                text += ch
        return root

