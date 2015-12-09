from alteraparser.parser import Parser
from alteraparser.bnf.grammar import bnf_grammar
from alteraparser.io.output import BufferedOutput
import re


class Generator(object):

    def __init__(self, output):
        self.__bnf_parser = Parser(bnf_grammar)

        self.__output = output
        self.__indent_level = 0
        self.__indent_size = 4

        self.__fn_id_creator = FnIdCreator()
        self.__functions = {}

        self.__edit_section_start = re.compile(r'\s*#--beginedit\s+(\S+)\s*$')
        self.__edit_section_end = re.compile(r'\s*#--endedit\s*$')

    def generate_parser(self, grammar_input_stream, edit_sections={}):
        self.__writeln('from alteraparser import *')
        self.__writeln('from alteraparser.ast import AST')
        self.__writeln('from alteraparser.parser import Parser')
        self.__writeln()
        self.__writeln()

        ast = self.__bnf_parser.parse(grammar_input_stream)
        grammar_name = self.__find_grammar_name(ast)
        self.__writeln("def create_{}_parser():".format(grammar_name))
        self.__indent()
        self.__writeln("return Parser({}())".format(grammar_name))
        self.__dedent()
        self.__writeln()
        self.__writeln()

        for node in ast.ast_children:
            if node.name == 'rule':
                self.__generate_rule(node, edit_sections)
            elif node.name == 'grammar':
                self.__generate_grammar(node, edit_sections)
        self.__generate_internal_functions()

    def __find_grammar_name(self, ast):
        for rule in ast.ast_children:
            if rule.name == 'grammar':
                return rule.ast_children[0].text
        return ''

    def __generate_grammar(self, grammar, edit_sections):
        name = grammar.ast_children[0].text.lower()
        self.__writeln("def _{}_trnsf(ast):".format(name))
        self.__indent()
        self.__generate_edit_section(name, edit_sections)
        self.__dedent()
        self.__writeln()
        self.__writeln()
        self.__writeln('def {}():'.format(name))
        node = grammar.ast_children[1]
        branches = []
        if node.name == 'branches':
            for it in node.ast_children:
                branches.append(it)
        else:
            branches.append(node)
        self.__indent()
        self.__writeln('branches = []')
        for branch in branches:
            call = self.__create_call(branch)
            self.__writeln('branches.append({})'.format(call))
        line = "return grammar('{0}', branches, _{0}_trnsf)".format(name)
        self.__writeln(line)
        self.__dedent()
        self.__writeln()
        self.__writeln()

    def __generate_edit_section(self, section_name, edit_sections):
        self.__writeln('#--beginedit {}'.format(section_name))
        if section_name in edit_sections:
            lines = edit_sections[section_name]
            for line in lines:
                self.__output.writeln(line) #<-- ignore indentation!
        else:
            self.__writeln('return ast')
        self.__writeln('#--endedit')

    def __generate_rule(self, rule, edit_sections):
        rule_name = rule.ast_children[0].text.lower()
        unique = rule.ast_children[2].text == 'true'
        self.__writeln("def _{}_trnsf(ast):".format(rule_name))
        self.__indent()
        self.__generate_edit_section(rule_name, edit_sections)
        self.__dedent()
        self.__writeln()
        self.__writeln()
        line = "@group(name='{0}', is_unique={1}, transform_ast_fn=_{0}_trnsf)".format(rule_name, unique)
        self.__writeln(line)
        line = 'def _{}(self, start, end):'.format(rule_name)
        self.__writeln(line)
        self.__indent()
        self.__generate_fn_body(rule.ast_children[1])
        self.__dedent()
        self.__writeln()
        self.__writeln()

    def __generate_fn_body(self, ast):
        body = self.__create_fn_body(ast)
        for line in body:
            self.__output.writeln(line)  # indentation already done

    def __create_fn_body(self, ast):
        saved_output = self.__output
        buf_output = BufferedOutput()
        self.__output = buf_output
        if ast.name == 'branches':
            self.__generate_branches_body(ast)
        elif ast.name == 'branch':
            self.__generate_branch_body(ast)
        elif ast.name == 'comp':
            self.__generate_comp_body(ast)
        else:
            self.__output.writeln('pass')
        self.__output = saved_output
        return buf_output.get_lines()

    def __create_call(self, ast):
        name = ast.name
        if name in ['branches', 'branch', 'comp']:
            call = '{}()'.format(self.__create_fn(ast))
        elif name == 'term':
            call = "keyword('{}')".format(ast.text)
        elif name == 'rule-name':
            call = '_{}()'.format(ast.own_text.lower())
        elif name == 'WHITESPACE':
            call = '_whitespace()'
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
            prev_cname = ''
            relevant_items = ['char', 'space', 'tab', 'newline']
            for char_node in char_nodes:
                cname = char_node.name
                if chars and prev_cname in relevant_items and cname in relevant_items:
                    chars += ', '
                if cname == 'char':
                    chars += "'{}'".format(char_node.text)
                elif cname in ['space', 'tab', 'newline']:
                    chars += "'{}'".format({
                                            'space': ' ',
                                            'tab': '\\t',
                                            'newline': '\\n'
                                            }[cname])
                prev_cname = cname
            call = "characters({})".format(chars)
            if negate:
                call += '.negate()'
        elif name in ['space', 'tab', 'newline']:
            call = "single_char('{}')".format({
                                                  'space': ' ',
                                                  'tab': '\\t',
                                                  'newline': '\\n'
                                              }[name])
        else:
            raise GeneratorError("Unsupported grammar element '{}'".format(name))
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
                res = 'optional({})'.format(call)
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
                'zero-to-one': 'optional',
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
                self.__writeln('curr = curr > many(_whitespace())')
            else:
                if prev_item and prev_item.name not in ['no-ws', 'optional-ws']:
                    self.__writeln('curr = curr > one_to_many(_whitespace())')
                call = self.__create_call(item)
                self.__writeln('curr = curr > {}'.format(call))
            prev_item = item
        self.__writeln('curr > end')

    def __generate_comp_body(self, comp):
        call = self.__create_call(comp.ast_children[0])
        self.__writeln('start > {} > end'.format(call))

    def __generate_internal_functions(self):
        fn_ids = list(self.__functions.keys())
        fn_ids.sort()
        for fn_id in fn_ids:
            self.__writeln('@group()')
            self.__writeln('def {}(self, start, end):'.format(fn_id))
            self.__indent()
            body = self.__functions[fn_id]
            for line in body:
                self.__output.writeln(line)
            self.__dedent()
            self.__writeln()
            self.__writeln()

    def __create_fn(self, ast):
        fn_id = self.__fn_id_creator.create_id(ast.name)
        self.__functions[fn_id] = self.__create_fn_body(ast)
        return fn_id

    def __indent(self):
        self.__indent_level += 1

    def __dedent(self):
        self.__indent_level -= 1

    def __writeln(self, text=''):
        text = self.__indent_level * self.__indent_size * ' ' + text
        self.__output.writeln(text)

    def scan_for_edit_sections(self, stream):
        edit_sections = {}
        section_name = ''
        lines = []
        line = ''
        while stream.has_next_char():
            ch = stream.get_next_char()
            if ch != '\n':
                line += ch
            else:
                if not section_name:
                    match = self.__edit_section_start.match(line)
                    if match:
                        section_name = match.group(1)
                        lines = []
                else:
                    match = self.__edit_section_end.match(line)
                    if match:
                        edit_sections[section_name] = lines
                        section_name = ''
                        lines = []
                    else:
                        lines.append(line)
                line = ''
        return edit_sections


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