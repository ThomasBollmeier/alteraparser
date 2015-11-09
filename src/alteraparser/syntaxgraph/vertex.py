from .abstract_vertex import AbstractVertex
from .dockable import Dockable


class VertexCategory:

    NORMAL = 1
    GROUP_START = 2
    GROUP_END = 3
    MATCHER = 4
    FINAL = 5


class Vertex(AbstractVertex, Dockable):

    def __init__(self, category = VertexCategory.NORMAL):
        AbstractVertex.__init__(self)
        self.__successors = []
        self._category = category

    def get_category(self):
        return self._category

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

    def _on_clone_creation(self, original):
        for successor in original.__successors:
            self.__successors.append(successor.clone())

