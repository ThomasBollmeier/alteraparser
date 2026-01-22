from alteraparser.ast_ import Ast
from alteraparser.grammar import GrammarNodeType, Grammar, GrammarNode, RuleStartNode, RuleEndNode
from alteraparser.lexer_grammar import LexerGrammar
from alteraparser.lexer import Lexer
from alteraparser.token_ import Token, TokenStream
from typing import List, Optional


class Parser:
    """A parser that processes tokens according to a grammar definition to build an AST.

    The Parser class implements a parsing algorithm that matches token sequences against
    grammar rules and constructs an Abstract Syntax Tree (AST) representing the parsed
    structure. It supports ambiguity detection and provides detailed error messages
    for syntax errors.

    Attributes:
        _grammar (Grammar): The grammar definition used for parsing.
    """

    def __init__(self, grammar: Grammar):
        """Initialize the parser with a grammar definition.

        Args:
            grammar (Grammar): The grammar definition that specifies the syntax rules
                             for parsing. Must be a valid Grammar instance.
        """
        self._grammar = grammar

    def parse(self, tokens: TokenStream) -> Optional[Ast]:
        """Parse a stream of tokens according to the grammar and return an AST.

        This method processes tokens sequentially, maintaining multiple possible parse
        paths simultaneously to handle ambiguous grammars. It uses backtracking to
        explore all valid parsing possibilities and constructs an Abstract Syntax Tree
        from the successful parse path.

        Args:
            tokens (TokenStream): A stream of tokens to be parsed. The stream should
                                contain tokens that match the grammar's terminal symbols.

        Returns:
            Ast: The root node of the Abstract Syntax Tree representing the parsed
                 structure. The AST follows the hierarchical structure defined by
                 the grammar rules.

        Raises:
            SyntaxError: If the token sequence doesn't match any valid grammar path,
                        if the parse is ambiguous (multiple valid interpretations),
                        or if the parse is incomplete (cannot reach the grammar end).
        """
        start_node = self._grammar.create_syntax_graph()
        matched_paths = [[start_node]]
        processed_tokens = []

        while True:
            expected_token = tokens.advance()
            if expected_token is None:
                break
            processed_tokens.append(expected_token)
            new_matched_paths = []
            for path in matched_paths:
                curr_node = path[-1]
                for token_types, follow_path in curr_node.find_follow_tokens(1):
                    if token_types[0] == expected_token.token_type:
                        new_path = path.copy()
                        # Avoid duplicating the current node if it's already the last in new_path
                        if new_path[-1] != follow_path[0]:
                            new_path.append(follow_path[0])
                        new_path.extend(follow_path[1:])
                        new_matched_paths.append(new_path)
            if not new_matched_paths:
                line = expected_token.line
                col = expected_token.column
                value = expected_token.value
                raise SyntaxError(f"Unexpected token @({line}, {col}): '{value}'")
            matched_paths = new_matched_paths

        # After processing all tokens, filter paths that can reach the end
        valid_matched_paths = []
        for path in matched_paths:
            path_to_end = self._grammar.find_path_to_end(path[-1])
            if path_to_end is not None:
                valid_matched_paths.append(path + path_to_end[1:])

        if len(valid_matched_paths) > 1:
            # Ambiguous parse
            raise SyntaxError("Ambiguous parse, multiple valid paths found")
        if not valid_matched_paths:
            raise SyntaxError("Incomplete parse, cannot reach end")

        return self._build_ast(valid_matched_paths[0], processed_tokens)

    @staticmethod
    def _build_ast(parse_path: List[GrammarNode], tokens: List[Token]) -> Optional[Ast]:
        """Build an Abstract Syntax Tree from a valid parse path and tokens.

        This method constructs the AST by walking through the parse path and
        correlating grammar nodes with their corresponding tokens. It uses a stack
        to maintain the hierarchical structure of nested rules and properly
        associates tokens with their parent rule nodes.

        Args:
            parse_path (List[GrammarNode]): A sequence of grammar nodes representing
                                           a valid parse path from start to end.
                                           Should include RULE_START, RULE_END, and
                                           TOKEN nodes in proper order.
            tokens (List[Token]): The list of tokens that were successfully parsed.
                                 These tokens correspond to TOKEN nodes in the parse path.

        Returns:
            Ast: The root node of the constructed Abstract Syntax Tree. Each rule
                 becomes an AST node with the rule name, and tokens become leaf nodes
                 with their values.

        Note:
            This is a static method as it doesn't depend on instance state and can
            be used independently for AST construction from any valid parse path.
        """
        ret = None
        ast_stack = []
        token_idx = 0

        for node in parse_path:
            if node.node_type == GrammarNodeType.RULE_START:
                start_node: RuleStartNode = node  # type: ignore
                ast_node = Ast(name=start_node.rule.name, id_=start_node.get_id())
                ast_stack.append(ast_node)
            elif node.node_type == GrammarNodeType.RULE_END:
                completed_ast = ast_stack.pop()
                end_node: RuleEndNode = node # type: ignore
                transformer = end_node.rule.grammar.get_ast_transformer(end_node.rule.name)
                if transformer:
                    id_ = completed_ast.id
                    completed_ast = transformer(completed_ast)
                    completed_ast.id = id_
                if ast_stack:
                    ast_stack[-1].add_child(completed_ast)
                else:
                    ret = completed_ast
            elif node.node_type == GrammarNodeType.TOKEN:
                token = tokens[token_idx]
                token_idx += 1
                ast_node = Ast(name=token.token_type, value=token.value, id_=node.get_id())
                if ast_stack:
                    ast_stack[-1].add_child(ast_node)

        return ret


class TextParser(Parser):
    """A parser that combines lexing and parsing to build an AST from raw text.

    The TextParser class first tokenizes the input text using a specified lexer grammar,
    then parses the resulting tokens according to a grammar definition to construct an
    Abstract Syntax Tree (AST). It handles both lexical and syntactical analysis, providing
    a complete parsing solution.

    Attributes:
        _lexer_grammar (LexerGrammar): The lexer grammar used for tokenization.
    """

    def __init__(self, grammar: Grammar, lexer_grammar: LexerGrammar):
        """Initialize the text parser with grammar and lexer grammar definitions.

        Args:
            grammar (Grammar): The grammar definition that specifies the syntax rules
                             for parsing. Must be a valid Grammar instance.
            lexer_grammar (LexerGrammar): The lexer grammar definition that specifies
                                         the tokenization rules. Must be a valid
                                         LexerGrammar instance.
        """
        super().__init__(grammar)
        self._lexer_grammar = lexer_grammar

    def parse_text(self, text: str) -> Optional[Ast]:
        """Parse raw text input to produce an Abstract Syntax Tree (AST).

        This method first tokenizes the input text using the defined lexer grammar,
        then parses the resulting tokens according to the grammar rules to build an AST.

        Args:
            text (str): The raw text input to be parsed.

        Returns:
            Ast: The root node of the Abstract Syntax Tree representing the parsed
                 structure.

        Raises:
            SyntaxError: If there are lexical or syntactical errors during parsing.
        """
        lexer = Lexer(self._lexer_grammar, text)
        return self.parse(lexer)