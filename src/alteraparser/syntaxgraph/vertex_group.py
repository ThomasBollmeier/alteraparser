from .dockable import Dockable
from .vertex import Vertex


class StartVertex(Vertex):

    def __init__(self, vertex_group):
        Vertex.__init__(self)
        self.__group = vertex_group

    def num_successors(self):
        if not self.__group._VertexGroup__expanded:
            self.__group.expand()
        return Vertex.num_successors(self)

    def nth_successor(self, idx):
        if not self.__group._VertexGroup__expanded:
            self.__group.expand()
        return Vertex.nth_successor(self, idx)


class VertexGroup(Dockable):

    def __init__(self):
        self.__expanded = False
        self.__start = StartVertex(self)
        self.__end = Vertex()

    def connect(self, dockable):
        self.__end.connect(dockable)
        return dockable

    def get_dock_vertex(self):
        return self.__start

    def expand(self):
        if not self.__expanded:
            self._on_expand(self.__start, self.__end)
            self.__expanded = True

    def _on_expand(self, start, end):
        pass
