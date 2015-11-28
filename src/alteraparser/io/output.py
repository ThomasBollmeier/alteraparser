import os


class Output(object):

    def write(self, text):
        pass

    def writeln(self, text):
        self.write(text + os.linesep)


class ConsoleOutput(Output):

    def write(self, text):
        print(text)

