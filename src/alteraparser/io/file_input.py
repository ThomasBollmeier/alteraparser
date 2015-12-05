from .input_stream import InputStream


class FileInput(InputStream):

    def __init__(self, file_path):
        f = open(file_path, 'r')
        self.__lines = f.readlines()
        f.close()
        self.__line_num = 0
        self.__col_num = 0

    def get_next_char(self):
        line = self.__lines[self.__line_num]
        next_char = line[self.__col_num]
        self.__col_num += 1
        if self.__col_num >= len(line):
            self.__line_num += 1
            self.__col_num = 0
        return next_char

    def has_next_char(self):
        if self.__line_num >= len(self.__lines):
            return False
        else:
            line = self.__lines[self.__line_num]
            return self.__col_num <= len(line) - 1
