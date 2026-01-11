import re
from typing import List, Tuple


class LexerGrammar:
    """
    A class to define lexer grammar rules for tokenization.
    """

    def __init__(self):
        self.rules: List[Tuple[str, re.Pattern, bool]] = []

    def add_rule(self, token_type: str, pattern: str, ignore: bool=False, case_insensitive: bool=False) -> 'LexerGrammar':
        if not pattern.startswith('^'):
            pattern = '^' + pattern
        if case_insensitive:
            regex = re.compile(pattern, re.IGNORECASE)
        else:
            regex = re.compile(pattern)
        self.rules.append((token_type, regex, ignore))
        return self

    def get_rules(self) -> List[Tuple[str, re.Pattern, bool]]:
        return self.rules

    def __getattr__(self, item):
        token_types = [rule[0] for rule in self.rules]
        if item in token_types:
            return item
        raise AttributeError(f"'LexerGrammar' object has no attribute '{item}'")