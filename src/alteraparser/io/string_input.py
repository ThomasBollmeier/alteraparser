from .input_stream import InputStream


class StringInput(InputStream):

    def __init__(self, string_data):
        self.__string_data = string_data
        self.__cursor = -1

    def get_next_char(self):
        self.__cursor += 1
        if self.__cursor < len(self.__string_data):
            return self.__string_data[self.__cursor]
        else:
            return None

    def has_next_char(self):
        return self.__cursor + 1 < len(self.__string_data)