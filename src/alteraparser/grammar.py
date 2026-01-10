from typing import List, Optional as Option, Tuple, Set, Callable
from enum import Enum
from alteraparser.ast_ import Ast


class GrammarNodeType(Enum):
    """Enumeration of different types of grammar nodes.

    Defines the different kinds of nodes that can exist in a grammar syntax graph,
    each serving a specific purpose in the parsing process.
    """
    NORMAL = 1  # Regular nodes for graph structure
    TOKEN = 2  # Nodes representing terminal symbols (tokens)
    RULE_START = 3  # Nodes marking the start of a grammar rule
    RULE_END = 4  # Nodes marking the end of a grammar rule


class GrammarNode:
    """A node in the grammar syntax graph representing a point in the parsing process.

    GrammarNodes form a directed graph structure that represents the grammar rules
    and their relationships. Each node has a type and can have child nodes,
    creating paths that the parser can follow.

    Attributes:
        node_type (GrammarNodeType): The type of this grammar node.
        token_type (str, optional): If this is a TOKEN node, the type of token it represents.
        children (List[GrammarNode]): List of child nodes in the syntax graph.
    """

    def __init__(self,
                 node_type: GrammarNodeType,
                 token_type: Option[str] = None):
        """Initialize a grammar node.

        Args:
            node_type (GrammarNodeType): The type of node being created.
            token_type (str, optional): For TOKEN nodes, specifies which token type
                                       this node represents. Ignored for other node types.
        """
        self.node_type = node_type
        self.token_type = token_type
        self.children: List[GrammarNode] = []

    def clone(self) -> 'GrammarNode':
        """Create a clone of this grammar node.

        Returns:
            GrammarNode: A new instance that is a copy of this node, without children.
        """
        return GrammarNode(self.node_type, self.token_type)

    def add_child(self, child_node: 'GrammarNode'):
        """Add a child node to this grammar node.

        Args:
            child_node (GrammarNode): The child node to add. This creates a directed
                                     edge from this node to the child node.
        """
        self.children.append(child_node)

    def get_children(self) -> List['GrammarNode']:
        """Get the list of child nodes.

        Returns:
            List[GrammarNode]: A list of all child nodes connected to this node.
        """
        return self.children

    def find_follow_tokens(self,
                           n: int = 1,
                           token_types: Option[List[str]] = None,
                           path: Option[List['GrammarNode']] = None,
                           skip_self: bool = True) -> List[Tuple[List[str], List['GrammarNode']]]:
        """Find all possible sequences of n tokens that can follow from this node.

        This method performs a depth-first search through the grammar graph to find
        all possible token sequences of length n that can be encountered when parsing
        continues from this node.

        Args:
            n (int): The number of tokens to look ahead. Default is 1.
            token_types (List[str], optional): Accumulated token types in the current path.
                                              Used for recursion, typically None for initial calls.
            path (List[GrammarNode], optional): Accumulated grammar nodes in the current path.
                                               Used for recursion, typically None for initial calls.
            skip_self (bool): Whether to skip including this node in the path initially.
                             Used to control recursion behavior.

        Returns:
            List[Tuple[List[str], List[GrammarNode]]]: A list of tuples where each tuple
            contains:
            - A list of token types that form a valid n-token sequence
            - The corresponding path of grammar nodes that leads to those tokens
        """
        if token_types is None:
            token_types = []
        if path is None:
            path = []

        results = []
        if self.node_type != GrammarNodeType.NORMAL:
            path = path + [self]

        if self.node_type == GrammarNodeType.TOKEN and not skip_self:
            token_types = token_types + [self.token_type]
            n -= 1
            if n == 0:
                results.append((token_types, path))
                return results

        for child in self.get_children():
            results.extend(child.find_follow_tokens(n, token_types, path, False))

        return results

    def find_epsilon_path(self,
                          end_reached: Callable[['GrammarNode'], bool],
                          path: Option[List['GrammarNode']] = None,
                          visited: Option[Set['GrammarNode']] = None) -> Option[List['GrammarNode']]:
        """Find a path from this node to a target node without consuming tokens.

        This method searches for an epsilon path (a path that doesn't require any tokens)
        from the current node to a node that satisfies the end condition. This is used
        to determine if parsing can reach a valid end state without consuming more tokens.

        Args:
            end_reached (Callable[[GrammarNode], bool]): A predicate function that returns
                                                        True when the target node is reached.
            path (List[GrammarNode], optional): Accumulated path for recursion.
                                               Should be None for initial calls.
            visited (Set[GrammarNode], optional): Set of already visited nodes to prevent
                                                 infinite loops. Should be None for initial calls.

        Returns:
            List[GrammarNode] or None: The path from this node to the target node if one exists,
                                      None if no such path exists.
        """
        if path is None:
            path = []
        if visited is None:
            visited = set()

        if self.node_type != GrammarNodeType.NORMAL:
            path = path + [self]
        visited.add(self)

        if end_reached(self):
            return path

        for child in self.get_children():
            if child not in visited and child.node_type != GrammarNodeType.TOKEN:
                result = child.find_epsilon_path(end_reached, path, visited)
                if result is not None:
                    return result

        return None

    def __repr__(self) -> str:
        """Return a string representation of the grammar node.

        Returns:
            str: A string representation showing the node type and token type if applicable.
        """
        if self.node_type == GrammarNodeType.TOKEN:
            return f'->[{self.token_type}]->'
        else:
            return '->'


class RuleStartNode(GrammarNode):
    """A grammar node that marks the beginning of a grammar rule.

    This specialized node type is used to denote where a grammar rule starts
    in the syntax graph. It contains a reference to the rule it represents
    and triggers rule expansion when accessed.

    Attributes:
        rule (Rule): The grammar rule that this node represents the start of.
    """

    def __init__(self, rule_object: 'Rule'):
        """Initialize a rule start node.

        Args:
            rule_object (Rule): The grammar rule that this node marks the start of.
        """
        GrammarNode.__init__(self, GrammarNodeType.RULE_START)
        self.rule = rule_object

    def clone(self) -> GrammarNode:
        """Create a clone of this rule start node.

        Returns:
            RuleStartNode: A new instance that is a copy of this node, without children.
        """
        return RuleStartNode(self.rule.clone())

    def get_children(self) -> List[GrammarNode]:
        """Get child nodes, ensuring the rule is expanded first.

        Returns:
            List[GrammarNode]: List of child nodes after ensuring rule expansion.
        """
        self.rule.expand()
        return super().get_children()

    def __repr__(self) -> str:
        """Return a string representation of the rule start node.

        Returns:
            str: A string showing this is the start of a named rule.
        """
        return f'->(Start {self.rule.name})->'


class RuleEndNode(GrammarNode):
    """A grammar node that marks the end of a grammar rule.

    This specialized node type is used to denote where a grammar rule ends
    in the syntax graph. It contains a reference to the rule it represents
    the end of.

    Attributes:
        rule (Rule): The grammar rule that this node represents the end of.
    """

    def __init__(self, rule_object: 'Rule'):
        """Initialize a rule end node.

        Args:
            rule_object (Rule): The grammar rule that this node marks the end of.
        """
        GrammarNode.__init__(self, GrammarNodeType.RULE_END)
        self.rule = rule_object

    def clone(self) -> GrammarNode:
        """Create a clone of this rule end node.

        Returns:
            RuleEndNode: A new instance that is a copy of this node, without children.
        """
        return RuleEndNode(self.rule.clone())

    def get_children(self) -> List[GrammarNode]:
        """Get child nodes.

        Returns:
            List[GrammarNode]: List of child nodes.
        """
        return super().get_children()

    def __repr__(self) -> str:
        """Return a string representation of the rule end node.

        Returns:
            str: A string showing this is the end of a named rule.
        """
        return f'->(End {self.rule.name})->'


class GrammarElement:
    """Abstract base class for all grammar elements.

    GrammarElements are building blocks of grammar rules that can be composed
    together to form complex grammar structures. Each element has an entry
    point (in_node) and an exit point (out_node) that allow them to be
    connected in a grammar graph.
    """

    def __init__(self):
        """Initialize a grammar element."""
        ...

    def get_in_node(self) -> GrammarNode:
        """Get the entry point node for this grammar element.

        Returns:
            GrammarNode: The node where parsing enters this element.

        Raises:
            NotImplementedError: This is an abstract method that must be implemented by subclasses.
        """
        raise NotImplementedError

    def get_out_node(self) -> GrammarNode:
        """Get the exit point node for this grammar element.

        Returns:
            GrammarNode: The node where parsing exits this element.

        Raises:
            NotImplementedError: This is an abstract method that must be implemented by subclasses.
        """
        raise NotImplementedError

    def clone(self) -> 'GrammarElement':
        """Create a clone of this grammar element.

        Returns:
            GrammarElement: A new instance that is a copy of this element.

        Raises:
            NotImplementedError: This is an abstract method that must be implemented by subclasses.
        """
        raise NotImplementedError


def connect(element1: GrammarElement, element2: GrammarElement):
    """Connect two grammar elements by linking their nodes.

    Creates a directed edge from the output node of element1 to the input
    node of element2, allowing parsing to flow from the first element to
    the second.

    Args:
        element1 (GrammarElement): The source element whose output will be connected.
        element2 (GrammarElement): The target element whose input will be connected to.
    """
    out_node = element1.get_out_node()
    in_node = element2.get_in_node()
    out_node.add_child(in_node)


class NormalElement(GrammarElement):
    """A grammar element that wraps a single grammar node.

    This element type is used to adapt existing GrammarNodes into the
    GrammarElement interface, where both the input and output point to
    the same node.

    Attributes:
        node (GrammarNode): The grammar node being wrapped.
    """

    def __init__(self, node: GrammarNode):
        """Initialize a normal element with a grammar node.

        Args:
            node (GrammarNode): The node to wrap as a grammar element.
        """
        GrammarElement.__init__(self)
        self.node = node

    def clone(self) -> GrammarElement:
        return NormalElement(self.node.clone())

    def get_in_node(self) -> GrammarNode:
        return self.node

    def get_out_node(self) -> GrammarNode:
        return self.node


class TokenElement(GrammarElement):
    """A grammar element representing a terminal token.

    TokenElements represent terminal symbols (tokens) in the grammar.
    They match specific token types during parsing and have no internal
    structure.

    Attributes:
        node (GrammarNode): The TOKEN node representing this terminal.
    """

    def __init__(self, token_type: str):
        """Initialize a token element.

        Args:
            token_type (str): The type of token this element represents.
        """
        GrammarElement.__init__(self)
        self.node = GrammarNode(GrammarNodeType.TOKEN, token_type)

    def clone(self) -> GrammarElement:
        return TokenElement(self.node.token_type)

    def get_in_node(self) -> GrammarNode:
        return self.node

    def get_out_node(self) -> GrammarNode:
        return self.node


def tok(token_type: str):
    """Create a TokenElement for the specified token type.

    This is a convenience factory function for creating TokenElements.

    Args:
        token_type (str): The type of token to create an element for.

    Returns:
        TokenElement: A new TokenElement for the specified token type.
    """
    return TokenElement(token_type)


class Sequence(GrammarElement):
    """A grammar element that matches a sequence of elements in order.

    Sequence elements connect multiple grammar elements in series, requiring
    all elements to match in the specified order. The sequence succeeds only
    if all its constituent elements match sequentially.

    Attributes:
        elements (List[GrammarElement]): The list of elements that must match in order.
    """

    def __init__(self, elements: List[GrammarElement]):
        """Initialize a sequence with a list of elements.

        Args:
            elements (List[GrammarElement]): The elements to match in sequence.
                                           Must be a non-empty list.
        """
        GrammarElement.__init__(self)
        self.elements = [element.clone() for element in elements]
        for i in range(len(self.elements) - 1):
            connect(self.elements[i], self.elements[i + 1])

    def clone(self) -> GrammarElement:
        return Sequence(self.elements)

    def get_in_node(self) -> GrammarNode:
        """Get the input node (first element's input).

        Returns:
            GrammarNode: The input node of the first element in the sequence.
        """
        return self.elements[0].get_in_node()

    def get_out_node(self) -> GrammarNode:
        """Get the output node (last element's output).

        Returns:
            GrammarNode: The output node of the last element in the sequence.
        """
        return self.elements[-1].get_out_node()


def seq(*elements: GrammarElement) -> Sequence:
    """Create a Sequence from multiple grammar elements.

    This is a convenience factory function for creating Sequence elements.

    Args:
        *elements: Variable number of grammar elements to sequence.

    Returns:
        Sequence: A new Sequence containing the specified elements.
    """
    return Sequence(list(elements))


class Choice(GrammarElement):
    """A grammar element that matches one of several alternative branches.

    Choice elements represent alternatives in the grammar, where exactly one
    of the provided branches must match. The choice succeeds if any of its
    branches matches successfully.

    Attributes:
        branches (List[GrammarElement]): The alternative branches to choose from.
        start_node (GrammarNode): Internal node that fans out to all branches.
        end_node (GrammarNode): Internal node that all branches converge to.
    """

    def __init__(self, branches: List[GrammarElement]):
        """Initialize a choice with a list of alternative branches.

        Args:
            branches (List[GrammarElement]): The alternative elements to choose from.
                                           Must be a non-empty list.
        """
        GrammarElement.__init__(self)
        self.branches = [branch.clone() for branch in branches]
        self.start_node = GrammarNode(GrammarNodeType.NORMAL)
        self.end_node = GrammarNode(GrammarNodeType.NORMAL)
        for branch in self.branches:
            self.start_node.add_child(branch.get_in_node())
            branch.get_out_node().add_child(self.end_node)

    def clone(self) -> GrammarElement:
        return Choice(self.branches)

    def get_in_node(self) -> GrammarNode:
        """Get the input node (the choice start node).

        Returns:
            GrammarNode: The internal start node that branches out to all alternatives.
        """
        return self.start_node

    def get_out_node(self) -> GrammarNode:
        """Get the output node (the choice end node).

        Returns:
            GrammarNode: The internal end node where all branches converge.
        """
        return self.end_node


def choice(*branches: GrammarElement) -> Choice:
    """Create a Choice from multiple grammar elements.

    This is a convenience factory function for creating Choice elements.

    Args:
        *branches: Variable number of grammar elements to choose from.

    Returns:
        Choice: A new Choice containing the specified branch alternatives.
    """
    return Choice(list(branches))


class Optional(GrammarElement):
    """A grammar element that optionally matches another element.

    Optional elements make their contained element optional - parsing can
    either match the element or skip it entirely. Both paths are valid.

    Attributes:
        start_node (GrammarNode): Internal node that can go to element or skip to end.
        end_node (GrammarNode): Internal node where both paths (match/skip) converge.
    """

    def __init__(self, element: GrammarElement):
        """Initialize an optional wrapper around an element.

        Args:
            element (GrammarElement): The element that is optional.
        """
        GrammarElement.__init__(self)
        self.element = element.clone()
        self.start_node = GrammarNode(GrammarNodeType.NORMAL)
        self.end_node = GrammarNode(GrammarNodeType.NORMAL)
        self.start_node.add_child(self.element.get_in_node())
        self.start_node.add_child(self.end_node)
        self.element.get_out_node().add_child(self.end_node)

    def clone(self) -> GrammarElement:
        return Optional(self.element.clone())

    def get_in_node(self) -> GrammarNode:
        """Get the input node (the optional start node).

        Returns:
            GrammarNode: The internal start node that can branch to element or skip.
        """
        return self.start_node

    def get_out_node(self) -> GrammarNode:
        """Get the output node (the optional end node).

        Returns:
            GrammarNode: The internal end node where both paths converge.
        """
        return self.end_node


def opt(element: GrammarElement) -> Optional:
    """Create an Optional wrapper around a grammar element.

    This is a convenience factory function for creating Optional elements.

    Args:
        element (GrammarElement): The element to make optional.

    Returns:
        Optional: A new Optional containing the specified element.
    """
    return Optional(element)


class Many(GrammarElement):
    """A grammar element that matches zero or more repetitions of another element.

    Many elements allow for repeated matching of their contained element.
    The element can match zero times (immediately proceed to end) or any
    number of times (loop back for more matches).

    Attributes:
        start_node (GrammarNode): Internal node that can go to element or end.
        end_node (GrammarNode): Internal node where the loop terminates.
    """

    def __init__(self, element: GrammarElement):
        """Initialize a many wrapper around an element.

        Args:
            element (GrammarElement): The element that can be repeated.
        """
        GrammarElement.__init__(self)
        self.element = element.clone()
        self.start_node = GrammarNode(GrammarNodeType.NORMAL)
        self.end_node = GrammarNode(GrammarNodeType.NORMAL)
        self.start_node.add_child(self.element.get_in_node())
        self.start_node.add_child(self.end_node)
        self.element.get_out_node().add_child(self.start_node)

    def clone(self) -> GrammarElement:
        return Many(self.element.clone())

    def get_in_node(self) -> GrammarNode:
        """Get the input node (the loop start node).

        Returns:
            GrammarNode: The internal start node that can loop or exit.
        """
        return self.start_node

    def get_out_node(self) -> GrammarNode:
        """Get the output node (the loop end node).

        Returns:
            GrammarNode: The internal end node where the loop exits.
        """
        return self.end_node


def many(element: GrammarElement) -> Many:
    """Create a Many wrapper around a grammar element.

    This is a convenience factory function for creating Many elements
    that match zero or more repetitions.

    Args:
        element (GrammarElement): The element to repeat.

    Returns:
        Many: A new Many containing the specified element.
    """
    return Many(element)


def one_or_more(element: GrammarElement) -> Sequence:
    """Create a pattern that matches one or more repetitions of an element.

    This combines the element with a Many wrapper to require at least
    one match while allowing unlimited additional matches.

    Args:
        element (GrammarElement): The element that must appear at least once.

    Returns:
        Sequence: A sequence of the element followed by zero or more repetitions.
    """
    return seq(element, many(element))


class Rule(GrammarElement):
    """A grammar element that represents a named rule with lazy expansion.

    Rules are the primary building blocks of grammars, representing named
    non-terminal symbols. They use lazy expansion to handle recursive
    definitions and circular references in the grammar.

    Attributes:
        grammar (Grammar): The grammar this rule belongs to.
        name (str): The name of this rule.
        expander (Callable): Function that defines the rule's content.
        is_expanded (bool): Whether this rule has been expanded yet.
        start_node (RuleStartNode): The node marking the rule's start.
        end_node (RuleEndNode): The node marking the rule's end.
    """

    def __init__(self,
                 grammar: 'Grammar',
                 name: str,
                 expander: Callable[['Grammar'], GrammarElement]
                 ):
        """Initialize a rule with its definition.

        Args:
            grammar (Grammar): The grammar this rule belongs to.
            name (str): The name identifier for this rule.
            expander (Callable): Function that returns the rule's grammar element
                               when called with the grammar as argument.
        """
        GrammarElement.__init__(self)
        self.grammar = grammar
        self.name = name
        self.expander = expander
        self.is_expanded = False
        self.start_node = RuleStartNode(self)
        self.end_node = RuleEndNode(self)

    def clone(self) -> GrammarElement:
        return Rule(self.grammar, self.name, self.expander)

    def get_in_node(self) -> GrammarNode:
        """Get the input node (the rule start node).

        Returns:
            GrammarNode: The RuleStartNode marking the beginning of this rule.
        """
        return self.start_node

    def get_out_node(self) -> GrammarNode:
        """Get the output node (the rule end node).

        Returns:
            GrammarNode: The RuleEndNode marking the end of this rule.
        """
        return self.end_node

    def expand(self):
        """Expand the rule definition if not already expanded.

        This method lazily expands the rule by calling the expander function
        and connecting the result between the rule's start and end nodes.
        Expansion only happens once to handle recursive rule definitions.
        """
        if not self.is_expanded:
            rule_root_elem = self.expander(self.grammar)
            start_elem = NormalElement(self.start_node)
            end_elem = NormalElement(self.end_node)
            connect(start_elem, rule_root_elem)
            connect(rule_root_elem, end_elem)
            self.is_expanded = True


# Decorator for rule expander functions
def rule(grammar: 'Grammar',
         name: str,
         is_start_rule: bool = False):
    """Decorator for defining grammar rules.

    This decorator allows defining grammar rules using Python functions.
    The decorated function should return a GrammarElement that defines
    the rule's structure.

    Args:
        grammar (Grammar): The grammar to add the rule to.
        name (str): The name of the rule.
        is_start_rule (bool): Whether this rule is the grammar's start rule.

    Returns:
        Callable: A decorator function that registers the rule with the grammar.
    """

    def wrapper(expander):
        grammar.add_rule(name, expander, is_start_rule)

    return wrapper


# Decorator for AST transformer functions
def ast_transformer(grammar: 'Grammar', rule_name: str):
    """Decorator for defining AST transformers for grammar rules.

    This decorator allows defining functions that transform the AST
    produced by parsing a specific rule. The decorated function should
    take an Ast node and return a transformed Ast node.

    Args:
        grammar (Grammar): The grammar to add the transformer to.
        rule_name (str): The name of the rule the transformer applies to.
    """

    def wrapper(transformer: Callable[['Ast'], 'Ast']) -> Callable[['Ast'], 'Ast']:
        grammar.add_ast_transformer(rule_name, transformer)
        return transformer

    return wrapper


class Grammar:
    """A complete grammar definition with rules and parsing infrastructure.

    The Grammar class manages a collection of named rules and provides the
    infrastructure for creating syntax graphs that can be used for parsing.
    It handles rule registration, start rule designation, and syntax graph
    creation.

    Attributes:
        rules (dict): Dictionary mapping rule names to their expander functions.
        ast_transformers (dict): Dictionary mapping rule names to their AST transformers.
        start_rule_name (str): Name of the rule that serves as the grammar's entry point.
        start_element (NormalElement): Internal element marking the global start.
        end_element (NormalElement): Internal element marking the global end.
        syntax_graph_created (bool): Whether the syntax graph has been built.
    """

    def __init__(self):
        """Initialize an empty grammar."""
        self.rules = {}
        self.ast_transformers = {}
        self.start_rule_name: Option[str] = None
        self.start_element = NormalElement(GrammarNode(GrammarNodeType.NORMAL))
        self.end_element = NormalElement(GrammarNode(GrammarNodeType.NORMAL))
        self.syntax_graph_created = False

    def set_start_rule(self, name: str):
        """Set the start rule for this grammar.

        Args:
            name (str): The name of the rule that should be the grammar's entry point.
        """
        self.start_rule_name = name

    def create_syntax_graph(self) -> GrammarNode:
        """Create and return the syntax graph for parsing.

        This method builds the complete syntax graph by connecting the start rule
        between the global start and end elements. The graph is built only once
        and subsequent calls return the same graph.

        Returns:
            GrammarNode: The root node of the syntax graph where parsing should begin.

        Raises:
            ValueError: If no start rule has been set.
        """
        if not self.syntax_graph_created:
            if self.start_rule_name is None:
                raise ValueError("Start rule not set.")
            start_rule = self.get_rule(self.start_rule_name)
            connect(self.start_element, start_rule)
            connect(start_rule, self.end_element)
            self.syntax_graph_created = True
        return self.start_element.get_in_node()

    def find_path_to_end(self, node: GrammarNode) -> Option[List[GrammarNode]]:
        """Find an epsilon path from a node to the grammar's end.

        Args:
            node (GrammarNode): The starting node to find a path from.

        Returns:
            List[GrammarNode] or None: A path from the node to the end if one exists,
                                      None otherwise.
        """
        end_node = self.end_element.get_out_node()
        return node.find_epsilon_path(lambda n: n is end_node)

    def add_rule(self,
                 name: str,
                 expander: Callable[['Grammar'], GrammarElement],
                 is_start_rule: bool = False):
        """Add a rule to this grammar.

        Args:
            name (str): The name identifier for the rule.
            expander (Callable): Function that defines the rule's grammar element.
            is_start_rule (bool): Whether this rule should be the start rule.
        """
        self.rules[name] = expander
        if is_start_rule:
            self.set_start_rule(name)

    def add_ast_transformer(self,
                            rule_name: str,
                            transformer: Callable[['Ast'], 'Ast']):
        """Add an AST transformer for a specific rule.

        Args:
            rule_name (str): The name of the rule the transformer applies to.
            transformer (Callable): Function that transforms the AST for the rule.
        """
        self.ast_transformers[rule_name] = transformer

    def get_rule(self, name: str) -> Rule:
        """Get a rule instance by name.

        Args:
            name (str): The name of the rule to retrieve.

        Returns:
            Rule: A Rule instance for the specified name.
        """
        expander = self.rules.get(name)
        return Rule(self, name, expander)

    def get_ast_transformer(self, rule_name: str) -> Option[Callable[['Ast'], 'Ast']]:
        """Get the AST transformer for a specific rule, if one exists.

        Args:
            rule_name (str): The name of the rule to get the transformer for.
        Returns:
            Callable[['Ast'], 'Ast'] or None: The transformer function if it exists, None otherwise.
        """
        return self.ast_transformers.get(rule_name)

    def __getitem__(self, item):
        """Get a rule using dictionary-style access (grammar['rule_name']).

        Args:
            item: The name of the rule to retrieve.

        Returns:
            Rule: A Rule instance for the specified name.
        """
        return self.get_rule(item)

    def __getattr__(self, item):
        """Get a rule using attribute-style access (grammar.rule_name).

        Args:
            item: The name of the rule to retrieve.

        Returns:
            Rule: A Rule instance for the specified name.
        """
        return self.get_rule(item)
