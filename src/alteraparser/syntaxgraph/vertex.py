
class Vertex(object):

    def __init__(self):
        self.__successors = []

    def add_successor(self, vertex):
        self.__successors.append(vertex)

    def num_successors(self):
        return len(self.__successors)

    def nth_successor(self, idx):
        if 0 <= idx < len(self.__successors):
            return self.__successors[idx]
        else:
            return None
