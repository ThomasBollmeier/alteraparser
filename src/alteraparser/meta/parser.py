from typing import List, Dict, Set, Tuple
from alteraparser.parser import TextParser as AlteraTextParser
from alteraparser.ast_ import Ast
from alteraparser.meta.lexer_grammar import LexerGrammar
from alteraparser.meta.grammar import create_meta_grammar


class Parser():

    def __init__(self):
        self._parser = AlteraTextParser(create_meta_grammar(), LexerGrammar())

    def parse(self, text: str):
        ast = self._parser.parse_text(text, rule_name="")
        if not ast:
            return ast
        macro_defs = self._read_macro_defs(ast)
        ast, _ = self._expand_macro_calls(ast, macro_defs)
        return Parser._remove_macro_defs(ast)

    @staticmethod
    def _remove_macro_defs(ast: Ast) -> Ast | None:
        if ast.name == "macro_def":
            return None
        new_children = []
        changed = False
        for child in ast.get_children():
            new_child = Parser._remove_macro_defs(child)
            if new_child:
                new_children.append(new_child)
            else:
                changed = True
        if not changed:
            return ast
        new_ast = ast.clone(deep=False)
        new_ast.children = new_children
        return new_ast

    def _expand_macro_calls(self, ast: Ast, macro_defs: Dict[str, '_Macro']) -> Tuple[Ast, bool]:
        if ast.name == "macro_call":
            return self._expand_macro(ast, macro_defs), True
        new_children = []
        expanded = False
        for child in ast.get_children():
            new_child, expanded_ = self._expand_macro_calls(child, macro_defs)
            if not expanded:
                expanded = expanded_
            new_children.append(new_child)
        if not expanded:
            return ast, expanded
        else:
            new_ast = ast.clone(deep=False)
            new_ast.children = new_children
            return new_ast, expanded

    def _expand_macro(self, ast: Ast, macro_defs: Dict[str, '_Macro']) -> Ast:
        name = ast.value
        if name not in macro_defs:
            raise Exception(f"Macro {name} not found")
        macro_def = macro_defs[name]
        expanded_args = []
        for ast in ast.get_children():
            new_ast, _ = self._expand_macro_calls(ast, macro_defs)
            expanded_args.append(new_ast)
        if len(expanded_args) != len(macro_def.params):
            raise Exception(f"Macro {name}: number of arguments does not match number of parameters")
        params_map = {
            param: expanded_args[i] for i, param in enumerate(macro_def.params)
        }
        return Parser._insert_args(macro_def.rhs, params_map)

    @staticmethod
    def _insert_args(ast: Ast, params_map: Dict[str, Ast]) -> Ast:
        if ast.name == "param_ref":
            param = ast.value
            if not param in params_map:
                raise Exception(f"Macro parameter {param} not found")
            return params_map[param]
        new_ast = ast.clone(deep=False)
        for child in ast.get_children():
            new_ast.add_child(Parser._insert_args(child, params_map))
        return new_ast

    def _read_macro_defs(self, ast: Ast) -> Dict[str, '_Macro']:
        ret = {}
        if ast.name == "macro_def":
            name = ast.get_attr("name")
            params = []
            for param_ast in ast[0]:
                params.append(param_ast.value)
            rhs = ast[1]
            self._adapt_param_refs(rhs, set(params))
            return {name: _Macro(name, params, rhs)}
        for child in ast.get_children():
            ret.update(self._read_macro_defs(child))
        return ret

    def _adapt_param_refs(self, ast: Ast, params: Set[str]):
        if ast.name == "rule":
            if ast.value in params:
                ast.name = "param_ref"
        for child in ast.get_children():
            self._adapt_param_refs(child, params)


class _Macro:
    def __init__(self, name: str, params: List[str], rhs: Ast):
        self.name = name
        self.params = params
        self.rhs = rhs
