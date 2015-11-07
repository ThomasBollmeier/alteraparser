from .dockable import Dockable
from .clonable import Clonable
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


class VertexGroup(Dockable, Clonable):

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

    def _on_clone_creation(self, original):
        pass


class Multiples(VertexGroup):

    def __init__(self, element=None, min_occur=0, max_occur=None):
        VertexGroup.__init__(self)
        self.__element = element
        self.__min_occur = min_occur
        self.__max_occur = max_occur

    def _on_expand(self, start, end):
        current = start
        for _ in range(self.__min_occur):
            current = current.connect(self.__element.clone())
        current.connect(end)
        if self.__max_occur is None:
            if current is not start:
                current.connect(current)
            else:
                start.connect(self.__element.clone()).connect(start)
        else:
            delta = self.__max_occur - self.__min_occur
            for _ in range(delta):
                current = current.connect(self.__element.clone())
                current.connect(end)

    def _on_clone_creation(self, original):
        VertexGroup._on_clone_creation(self, original)
        self.__element = original.__element.clone()
        self.__min_occur = original.__min_occur
        self.__max_occur = original.__max_occur


class Branches(VertexGroup):

    def __init__(self):
        VertexGroup.__init__(self)
        self.__branches = []

    def add_branch(self, elements):
        self.__branches.append(elements)

    def _on_expand(self, start, end):
        for branch in self.__branches:
            curr = start
            for elem in branch:
                curr = curr.connect(elem)
            curr.connect(end)

    def _on_clone_creation(self, original):
        VertexGroup._on_clone_creation(self, original)
        self.__branches = [[el.clone() for el in orig_branch] for orig_branch in original.__branches]


def optional(element):
    return Multiples(element, max_occur=1)


def many(element):
    return Multiples(element)


def one_to_many(element):
    return Multiples(element, min_occur=1)


def fork(*branches):
    res = Branches()
    for branch in branches:
        res.add_branch(branch)
    return res