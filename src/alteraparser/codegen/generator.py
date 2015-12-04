from alteraparser.parser import Parser
from alteraparser.bnf.grammar import bnf_grammar


class Generator(object):

    def __init__(self, output):
        self.__bnf_parser = Parser(bnf_grammar)
        self.__output = output
        self.__indent_level = 0
        self.__fn_id_creator = FnIdCreator()
        self.__functions = {}

    def generate_parser(self, grammar_input_stream):
        self.__writeln('from alteraparser import *')
        self.__writeln('from alteraparser.ast import AST')
        self.__writeln()
        self.__writeln()
        ast = self.__bnf_parser.parse(grammar_input_stream)
        for rule in ast.ast_children:
            self.__generate_rule(rule)
        self.__generate_internal_functions()

    def __generate_rule(self, rule):
        rule_name = rule.ast_children[0].text.lower()
        unique = rule.ast_children[2].text == 'true'
        line = "@group(name='{}', is_unique={})".format(rule_name, unique)
        self.__writeln(line)
        fn_name = rule_name
        if rule.name != 'grammar':
            fn_name = '_' + fn_name
        line = 'def {}(self, start, end):'.format(fn_name)
        self.__writeln(line)
        self.__indent()
        self.__generate_fn_body(rule.ast_children[1])
        self.__dedent()
        self.__writeln()
        self.__writeln()

    def __generate_fn_body(self, ast):
        if ast.name == 'branches':
            self.__generate_branches_body(ast)
        elif ast.name == 'branch':
            self.__generate_branch_body(ast)
        else:
            self.__writeln('pass')

    def __create_call(self, ast):
        name = ast.name
        if name in ['branch']:
            call = '{}()'.format(self.__create_fn(ast))
        elif name == 'term':
            call = "keyword('{}')".format(ast.text)
        elif name == 'rule-name':
            call = '_{}()'.format(ast.own_text.lower())
        elif name == 'range':
            ch_from = ast['from'][0].text
            ch_to = ast['to'][0].text
            call = "char_range('{}', '{}')".format(ch_from, ch_to)
        elif name == 'charset':
            negate = ast['negate']
            if not negate:
                char_nodes = ast.ast_children
            else:
                char_nodes = ast.ast_children[1:]
            chars = ''
            for char_node in char_nodes:
                if chars:
                    chars += ', '
                if char_node.name == 'char':
                    chars += "'{}'".format(char_node.text)
                elif char_node.name in ['space', 'tab', 'newline']:
                    chars += "'[]'".format({
                                            'space': ' ',
                                            'tab': '\t',
                                            'newline': '\n'
                                            }[char_node.name])
            call = "characters({})".format(chars)
            if negate:
                call += '.negate()'
        else:
            call = '<todo>()'
        id_nodes = ast['id']
        if id_nodes:
            id_node = id_nodes[0]
            call = self.__add_id(call, id_node)
        card = ast['cardinality']
        if card:
            call = self.__add_cardinality(call, card[0])
        return call

    def __add_cardinality(self, call, card):
        use_whitespace = len(card.ast_children) == 1
        mult = card.ast_children[0]
        if use_whitespace:
            ws = 'one_to_many(_whitespace())'
            if mult.name == 'zero-to-one':
                res = call
            elif mult.name == 'one-to-many':
                res = 'fork([{0}, many(fork([{1}, {0}]))])'.format(call, ws)
            elif mult.name == 'many':
                res = 'optional(fork([{0},'.format(call)
                res += ' many(fork([{0}, {1}]))]))'.format(ws, call)
            else:
                raise GeneratorError()
            return res
        else:
            fn_name = {
                'zero-to-one': 'zero_to_one',
                'one-to-many': 'one_to_many',
                'many': 'many'
            }[mult.name]
            return '{}({})'.format(fn_name, call)

    def __add_id(self, call, id_node):
        return "{}.set_id('{}')".format(call, id_node.text)

    def __generate_branches_body(self, branches):
        for branch in branches.ast_children:
            call = self.__create_call(branch)
            self.__writeln('start > {} > end'.format(call))

    def __generate_branch_body(self, branch):
        self.__writeln('curr = start')
        prev_item = None
        for item in branch.ast_children:
            if item.name == 'no-ws':
                pass
            elif item.name == 'optional-ws':
                self.__writeln('curr = curr > zero_to_many(_whitespace())')
            else:
                if prev_item and prev_item.name not in ['no-ws', 'optional-ws']:
                    self.__writeln('curr = curr > one_to_many(_whitespace())')
                call = self.__create_call(item)
                self.__writeln('curr = curr > {}'.format(call))
            prev_item = item
        self.__writeln('curr > end')

    def __generate_internal_functions(self):
        fn_ids = list(self.__functions.keys())
        fn_ids.sort()
        for fn_id in fn_ids:
            self.__writeln('def {}():'.format(fn_id))
            self.__indent()
            self.__generate_fn_body(self.__functions[fn_id])
            self.__dedent()
            self.__writeln()
            self.__writeln()

    def __create_fn(self, ast):
        fn_id = self.__fn_id_creator.create_id(ast.name)
        self.__functions[fn_id] = ast
        return fn_id

    def __indent(self):
        self.__indent_level += 1

    def __dedent(self):
        self.__indent_level -= 1

    def __writeln(self, text=''):
        text = self.__indent_level * '\t' + text
        self.__output.writeln(text)


class FnIdCreator(object):

    def __init__(self):
        self.__ids = {}

    def create_id(self, prefix):
        if prefix in self.__ids:
            id_ = self.__ids[prefix] + 1
        else:
            id_ = 1
        self.__ids[prefix] = id_
        return '_{}_{}'.format(prefix, id_)


class GeneratorError(Exception):
    pass