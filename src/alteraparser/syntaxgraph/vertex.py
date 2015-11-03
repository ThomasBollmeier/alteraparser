from .abstract_vertex import AbstractVertex
from .dockable import Dockable


class Vertex(AbstractVertex, Dockable):

    def __init__(self):
        self.__successors = []

    def num_successors(self):
        return len(self.__successors)

    def nth_successor(self, idx):
        if 0 <= idx < len(self.__successors):
            return self.__successors[idx]
        else:
            return None

    def connect(self, dockable):
        self.__successors.append(dockable.get_dock_vertex())
        return dockable

    def get_dock_vertex(self):
        return self

