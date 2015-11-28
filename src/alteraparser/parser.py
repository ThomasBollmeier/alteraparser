from alteraparser.ast import AST, TextNode
from alteraparser.io.string_input import StringInput
from alteraparser.syntaxgraph.match_finder import MatchFinder


class ParseError(RuntimeError):
    pass


class Parser(object):

    def __init__(self, grammar):
        self.__grammar = grammar

    def parse(self, input_stream):
        finder = MatchFinder(input_stream)
        self.__grammar.get_dock_vertex().walk(finder)
        if not finder.stopped:
            return self.__create_ast(finder.path)
        else:
            raise ParseError(self.__get_unparsed_text(finder.path))

    def parse_string(self, code_str):
        return self.parse(StringInput(code_str))

    def parse_file(self, file_path):
        f = open(file_path, "r")
        code_lines = f.readlines()
        f.close()
        code = ''.join(code_lines)
        return self.parse_string(code)

    @staticmethod
    def __create_ast(path):
        root = None
        stack = []
        text = ''
        for vertex, ch in path:
            if vertex.is_group_start():
                if text and stack:
                    parent = stack[-1]
                    parent.add_child(TextNode(text))
                text = ''
                node = AST(vertex.name, vertex.id)
                stack.append(node)
            elif vertex.is_group_end():
                node = stack.pop()
                node.add_child(TextNode(text))
                text = ''
                id_ = node.id
                transformed_node = vertex.transform_ast_fn(node)
                # ID must not be changed!
                transformed_node.id = id_
                if stack:
                    parent = stack[-1]
                    if not vertex.ignore:
                        parent.add_child(transformed_node)
                else:
                    root = transformed_node
            if ch is not None:
                text += ch
        return root

    @staticmethod
    def __get_unparsed_text(path):
        return ''.join([ch for _, ch in path if ch is not None])
