
class Processor(object):

    def process(self, vertex, path):
        pass

    def undo(self, vertex, path):
        pass


class ProcessingResult:

    CONTINUE = 0
    GO_BACK = 1
    STOP = 2