from typing import Optional


class Token:
    def __init__(self, token_type: str, value: str, line: int, column: int):
        self.token_type = token_type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self) -> str:
        return f'Token({self.token_type}, {self.value}, {self.line}, {self.column})'


class TokenStream:
    def advance(self) -> Optional[Token]:
        return None


class TokenStreamFromList(TokenStream):
    def __init__(self, tokens: list[Token]):
        self._tokens = tokens
        self._index = 0

    def advance(self) -> Optional[Token]:
        if self._index < len(self._tokens):
            token = self._tokens[self._index]
            self._index += 1
            return token
        return None

