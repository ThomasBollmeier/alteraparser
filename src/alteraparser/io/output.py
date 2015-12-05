import os


class Output(object):

    def write(self, text):
        pass

    def writeln(self, text=''):
        self.write(text + os.linesep)


class ConsoleOutput(Output):

    def write(self, text):
        print(text, end='')


class BufferedOutput(Output):

    def __init__(self):
        self.__line = ''
        self.__lines = []

    def write(self, text):
        self.__line += text

    def writeln(self, text=''):
        self.__line += text
        self.__lines.append(self.__line)
        self.__line = ''

    def get_lines(self):
        if self.__line:
            return self.__lines +  [self.__line]
        else:
            return self.__lines


class FileOutput(Output):

    def __init__(self, file_path):
        self.__file_path = file_path
        self.__file = None

    def open(self):
        if self.__file:
            self.__file.close()
        self.__file = open(self.__file_path, 'w')

    def close(self):
        self.__file.close()
        self.__file = None

    def write(self, text):
        self.__file.write(text)