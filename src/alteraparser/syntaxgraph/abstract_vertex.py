from .processor import ProcessingResult
from .clonable import Clonable


class AbstractVertex(Clonable):

    def __init__(self):
        Clonable.__init__(self)

    def num_successors(self):
        raise NotImplemented

    def nth_successor(self, idx):
        raise NotImplemented

    def walk(self, processor):
        path = []
        current = self
        result = None
        while True:
            result = processor.process(current, path)
            if result in [ProcessingResult.CONTINUE, None]:
                next = self.__continue(current, path)
                if not next:
                    next = self.__back(path, processor)
            elif result == ProcessingResult.GO_BACK:
                next = self.__back(path, processor)
            else:
                break
            if next is None:
                break
            current = next
        return result

    @staticmethod
    def __continue(current, path):
        if current.num_successors() > 0:
            next = current.nth_successor(0)
            path.append((current, 0))
        else:
            next = None
        return next

    @staticmethod
    def __back(path, processor):
        next_vertex = None
        while path:
            vertex, idx = path.pop()
            if idx < vertex.num_successors() - 1:
                next_vertex = vertex.nth_successor(idx + 1)
                path.append((vertex, idx + 1))
                return next_vertex
            else:
                processor.undo(vertex, path)
        return next_vertex

