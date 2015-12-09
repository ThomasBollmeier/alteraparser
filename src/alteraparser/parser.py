from alteraparser.ast import AST, TextNode
from alteraparser.io.string_input import StringInput
from alteraparser.syntaxgraph.match_finder import MatchFinder


class ParseError(RuntimeError):
    pass


class Parser(object):

    def __init__(self, grammar):
        self.__grammar = grammar
        self.__debug = False

    def debug_mode(self, debug=True):
        self.__debug = debug
        return self

    def parse(self, input_stream):
        finder = MatchFinder(input_stream).debug_mode(self.__debug)
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

    def __create_ast(self, path):
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
                if self.__debug and vertex.name:
                    print('PUSH -> {}'.format(vertex.name))
                    print(self.__stack_to_string(stack))
            elif vertex.is_group_end():
                node = stack.pop()
                if self.__debug and vertex.name:
                    print('POP <- {}'.format(vertex.name))
                    print(self.__stack_to_string(stack))
                    print("TEXT: '{}'".format(text))
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

    @staticmethod
    def __stack_to_string(stack):
        res = [node.name for node in stack if node.name]
        res = '[' + ','.join(res) + ']'
        return res
